from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from novel_pipeline.files import append_jsonl_line
from novel_pipeline.types import RunRecord


class LedgerError(RuntimeError):
    pass


class LedgerDecodeError(LedgerError):
    pass


_TIMED_STAGES = ("translating", "refining", "qa", "formatting")
_NON_PROVIDER_NAMES = {"", "cache", "local", "local_recovery", "manual", "rules"}


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _nonnegative_duration(value: Any) -> float | None:
    if isinstance(value, (int, float)) and value >= 0:
        return float(value)
    return None


def summarize_chapter_timings(records: Iterable[RunRecord]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[RunRecord]] = {}
    for record in records:
        if record.stage not in _TIMED_STAGES or "-block-" not in record.block_id:
            continue
        chapter_id = record.block_id.split("-block-", 1)[0]
        grouped.setdefault(chapter_id, []).append(record)

    summaries: dict[str, dict[str, Any]] = {}
    for chapter_id, chapter_records in sorted(grouped.items()):
        starts: list[datetime] = []
        finishes: list[datetime] = []
        stage_seconds = {stage: 0.0 for stage in _TIMED_STAGES}
        provider_stage_seconds: dict[str, dict[str, float]] = {
            stage: {} for stage in _TIMED_STAGES
        }
        provider_seconds = 0.0
        failed_provider_seconds = 0.0
        retry_provider_seconds = 0.0
        provider_calls = 0
        duration_records = 0
        failure_count = 0
        retry_count = 0
        explicit_qa_retries: dict[str, int] = {}
        inferred_qa_retries: dict[str, int] = {}

        for record in chapter_records:
            metadata = record.metadata
            duration = _nonnegative_duration(metadata.get("duration_seconds"))
            finished = _parse_timestamp(metadata.get("finished_at")) or _parse_timestamp(record.created_at)
            started = _parse_timestamp(metadata.get("started_at"))
            if started is None and finished is not None and duration is not None:
                started = finished - timedelta(seconds=duration)
            if started is None:
                started = _parse_timestamp(record.created_at)
            if started is not None:
                starts.append(started)
            if finished is not None:
                finishes.append(finished)

            is_provider = record.provider not in _NON_PROVIDER_NAMES
            if is_provider:
                provider_calls += 1
            if duration is not None:
                duration_records += 1
                stage_seconds[record.stage] += duration
                if is_provider:
                    provider_seconds += duration
                    provider_stage_seconds[record.stage][record.provider] = (
                        provider_stage_seconds[record.stage].get(record.provider, 0.0) + duration
                    )
                    if record.status in {"failed", "hard_fail"}:
                        failed_provider_seconds += duration
                    if record.status == "retry" or metadata.get("retry_from_qa"):
                        retry_provider_seconds += duration

            if record.status in {"failed", "hard_fail"}:
                failure_count += 1
            if record.status == "retry":
                retry_count += 1
                if record.stage == "qa":
                    explicit_qa_retries[record.block_id] = explicit_qa_retries.get(record.block_id, 0) + 1
            if record.stage == "qa" and record.status == "completed":
                raw_retry_count = metadata.get("retry_count", 0)
                if isinstance(raw_retry_count, int) and raw_retry_count > 0:
                    inferred_qa_retries[record.block_id] = max(
                        inferred_qa_retries.get(record.block_id, 0),
                        raw_retry_count,
                    )
                    if duration is not None and is_provider:
                        retry_provider_seconds += duration

            attempts = metadata.get("provider_attempts")
            if isinstance(attempts, list):
                for attempt in attempts:
                    if not isinstance(attempt, Mapping):
                        continue
                    attempt_duration = _nonnegative_duration(attempt.get("duration_seconds"))
                    provider_calls += 1
                    retry_count += 1
                    if attempt_duration is not None:
                        attempt_provider = str(attempt.get("provider") or record.provider or "unknown")
                        provider_seconds += attempt_duration
                        failed_provider_seconds += attempt_duration
                        retry_provider_seconds += attempt_duration
                        stage_seconds[record.stage] += attempt_duration
                        provider_stage_seconds[record.stage][attempt_provider] = (
                            provider_stage_seconds[record.stage].get(attempt_provider, 0.0)
                            + attempt_duration
                        )

        for block_id, inferred in inferred_qa_retries.items():
            retry_count += max(0, inferred - explicit_qa_retries.get(block_id, 0))

        started_at = min(starts) if starts else None
        finished_at = max(finishes) if finishes else None
        elapsed = (
            max(0.0, (finished_at - started_at).total_seconds())
            if started_at is not None and finished_at is not None
            else 0.0
        )
        summaries[chapter_id] = {
            "started_at": started_at.isoformat() if started_at is not None else "",
            "finished_at": finished_at.isoformat() if finished_at is not None else "",
            "wall_clock_seconds": elapsed,
            "provider_seconds": provider_seconds,
            "failed_provider_seconds": failed_provider_seconds,
            "retry_provider_seconds": retry_provider_seconds,
            "stage_seconds": stage_seconds,
            "provider_stage_seconds": provider_stage_seconds,
            "block_count": len({record.block_id for record in chapter_records}),
            "provider_call_count": provider_calls,
            "duration_record_count": duration_records,
            "retry_count": retry_count,
            "failure_count": failure_count,
        }
    return summaries


@dataclass(slots=True)
class ResumeState:
    run_id: str
    records: tuple[RunRecord, ...] = ()
    latest_by_block: dict[str, RunRecord] = field(default_factory=dict)
    latest_by_stage: dict[tuple[str, str], RunRecord] = field(default_factory=dict)
    records_by_block: dict[str, list[RunRecord]] = field(default_factory=dict)

    def committed(self, block_id: str, stage: str, status: str = "completed") -> bool:
        record = self.latest_by_stage.get((block_id, stage))
        return record is not None and record.status == status

    def latest_record(self, block_id: str) -> RunRecord | None:
        return self.latest_by_block.get(block_id)

    def records_for_block(self, block_id: str) -> tuple[RunRecord, ...]:
        return tuple(self.records_by_block.get(block_id, ()))

    def next_pending_stage(
        self,
        block_id: str,
        stage_order: Iterable[str],
        *,
        committed_status: str = "completed",
    ) -> str | None:
        for stage in stage_order:
            record = self.latest_by_stage.get((block_id, stage))
            if record is None:
                return stage
            if record.status == committed_status:
                continue
            if stage == "qa" and record.status in {"force_accepted", "skipped"}:
                continue
            if not self.committed(block_id, stage, committed_status):
                return stage
        return None

    def completed_blocks(self) -> tuple[str, ...]:
        return tuple(
            block_id
            for (block_id, stage), record in self.latest_by_stage.items()
            if stage == "completed" and record.status == "completed"
        )

    def failed_blocks(self) -> tuple[str, ...]:
        failed: set[str] = set()
        for (block_id, _stage), record in self.latest_by_stage.items():
            if record.status in {"failed", "hard_fail"}:
                failed.add(block_id)
        return tuple(sorted(failed))


@dataclass(slots=True)
class RunLedger:
    path: Path

    def append(self, record: RunRecord) -> RunRecord:
        if not record.run_id:
            raise LedgerError("RunRecord.run_id is required.")
        if not record.block_id:
            raise LedgerError("RunRecord.block_id is required.")
        if not record.stage:
            raise LedgerError("RunRecord.stage is required.")
        if not record.status:
            raise LedgerError("RunRecord.status is required.")
        append_jsonl_line(self.path, record)
        return record

    def append_stage(
        self,
        *,
        run_id: str,
        block_id: str,
        stage: str,
        status: str,
        provider: str = "",
        input_hash: str = "",
        output_hash: str = "",
        metadata: Mapping[str, Any] | None = None,
        created_at: str | None = None,
    ) -> RunRecord:
        record = RunRecord.new(
            run_id=run_id,
            block_id=block_id,
            stage=stage,
            status=status,
            provider=provider,
            input_hash=input_hash,
            output_hash=output_hash,
            metadata=metadata,
            created_at=created_at,
        )
        return self.append(record)

    def iter_records(
        self,
        *,
        run_id: str | None = None,
        block_id: str | None = None,
        stage: str | None = None,
        status: str | None = None,
    ) -> Iterator[RunRecord]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                payload = line.strip()
                if not payload:
                    continue
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError as exc:
                    raise LedgerDecodeError(
                        f"Invalid JSON in ledger {self.path} at line {line_number}."
                    ) from exc
                record = _run_record_from_mapping(data)
                if run_id is not None and record.run_id != run_id:
                    continue
                if block_id is not None and record.block_id != block_id:
                    continue
                if stage is not None and record.stage != stage:
                    continue
                if status is not None and record.status != status:
                    continue
                yield record

    def load_state(self, run_id: str) -> ResumeState:
        records = tuple(self.iter_records(run_id=run_id))
        latest_by_block: dict[str, RunRecord] = {}
        latest_by_stage: dict[tuple[str, str], RunRecord] = {}
        records_by_block: dict[str, list[RunRecord]] = {}
        for record in records:
            latest_by_block[record.block_id] = record
            latest_by_stage[(record.block_id, record.stage)] = record
            records_by_block.setdefault(record.block_id, []).append(record)
        return ResumeState(
            run_id=run_id,
            records=records,
            latest_by_block=latest_by_block,
            latest_by_stage=latest_by_stage,
            records_by_block=records_by_block,
        )

    def has_committed(
        self,
        *,
        run_id: str,
        block_id: str,
        stage: str,
        status: str = "completed",
    ) -> bool:
        state = self.load_state(run_id)
        return state.committed(block_id, stage, status)

    def latest_for_block(self, *, run_id: str, block_id: str) -> RunRecord | None:
        state = self.load_state(run_id)
        return state.latest_record(block_id)

    def pending_stage(
        self,
        *,
        run_id: str,
        block_id: str,
        stage_order: Iterable[str],
        committed_status: str = "completed",
    ) -> str | None:
        state = self.load_state(run_id)
        return state.next_pending_stage(block_id, stage_order, committed_status=committed_status)


def _run_record_from_mapping(data: Mapping[str, Any]) -> RunRecord:
    metadata = data.get("metadata", {})
    return RunRecord(
        run_id=str(data.get("run_id", "")),
        block_id=str(data.get("block_id", "")),
        stage=str(data.get("stage", "")),
        status=str(data.get("status", "")),
        created_at=str(data.get("created_at", "")),
        provider=str(data.get("provider", "")),
        input_hash=str(data.get("input_hash", "")),
        output_hash=str(data.get("output_hash", "")),
        metadata={str(key): value for key, value in dict(metadata).items()},
    )


__all__ = [
    "LedgerDecodeError",
    "LedgerError",
    "ResumeState",
    "RunLedger",
    "summarize_chapter_timings",
]
