from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from novel_pipeline.files import append_jsonl_line
from novel_pipeline.types import RunRecord


class LedgerError(RuntimeError):
    pass


class LedgerDecodeError(LedgerError):
    pass


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
]
