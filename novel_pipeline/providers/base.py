from __future__ import annotations

import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from novel_pipeline.types import ProviderRequest, ProviderResponse, ProviderSpec


class ProviderExecutionError(RuntimeError):
    def __init__(self, response: ProviderResponse, message: str | None = None) -> None:
        self.response = response
        super().__init__(message or f"Provider '{response.provider}' exited with code {response.returncode}.")


class ProviderOutputError(ProviderExecutionError):
    """Raised when a provider process exits but its output is not usable."""


_FAILURE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("quota", re.compile(r"\b(hit your limit|usage limit|rate limit|quota|too many requests|429|resource exhausted|exceeded your current quota|no capacity available|model_capacity_exhausted)\b", re.I)),
    ("refusal", re.compile(r"\b(i can(?:not|'t)|i am unable|as an ai|cannot assist|can't assist)\b", re.I)),
    ("auth", re.compile(r"\b(unauthorized|permission denied|authentication|not logged in|api key)\b", re.I)),
)


def default_provider_specs() -> dict[str, ProviderSpec]:
    return {
        "qwen": ProviderSpec(
            name="qwen",
            executable=("qwen",),
            prompt_flag=None,
            prompt_position="positional",
            model_flag="-m",
            model_position="before_prompt",
            default_model="deepseek-reasoner",
            timeout_seconds=300.0,
        ),
        "gemini": ProviderSpec(
            name="gemini",
            executable=("gemini",),
            prompt_flag="-p",
            prompt_position="flag",
            model_flag="--model",
            default_model="pro",
            timeout_seconds=300.0,
        ),
        "claude": ProviderSpec(
            name="claude",
            executable=("claude",),
            prompt_flag="-p",
            prompt_position="flag",
            model_flag="--model",
            default_model="sonnet",
            timeout_seconds=300.0,
        ),
        "codex": ProviderSpec(
            name="codex",
            executable=("codex", "exec"),
            prompt_flag=None,
            prompt_position="positional",
            model_flag="--model",
            default_model="",
            timeout_seconds=300.0,
        ),
    }


def build_provider_spec(name: str, data: Mapping[str, Any] | None = None, *, base_dir: Path | None = None) -> ProviderSpec:
    defaults = default_provider_specs().get(name)
    if defaults is None:
        defaults = ProviderSpec(name=name, executable=(name,))
    if data is None:
        return defaults
    payload = defaults.to_dict()
    payload.update({str(key): value for key, value in dict(data).items()})
    return ProviderSpec.from_mapping(name, payload, base_dir=base_dir)


@dataclass(slots=True)
class ProviderRunner:
    spec: ProviderSpec

    def build_command(self, request: ProviderRequest) -> list[str]:
        if not request.provider:
            request = ProviderRequest(
                prompt=request.prompt,
                provider=self.spec.name,
                stage=request.stage,
                model=request.model,
                cwd=request.cwd,
                timeout_seconds=request.timeout_seconds,
                env=dict(request.env),
                extra_args=tuple(request.extra_args),
            )
        return self.spec.build_command(request)

    def _estimate_windows_command_length(self, args: list[str]) -> int:
        """Return a conservative estimate of Windows command line length."""
        total = 0
        for arg in args:
            total += len(arg)
            if " " in arg or '"' in arg:
                total += 2  # quotes
        if args:
            total += len(args) - 1  # spaces between args
        return total

    def _sanitize_command_with_long_prompt(self, command: list[str], prompt: str) -> list[str]:
        """Replace the prompt argument with a marker to avoid huge logs."""
        marker = f"<PROMPT OMITTED: {len(prompt)} chars>"
        sanitized = []
        for arg in command:
            if arg == prompt:
                sanitized.append(marker)
            else:
                sanitized.append(arg)
        return sanitized

    def run(
        self,
        request: ProviderRequest,
        *,
        check: bool = False,
    ) -> ProviderResponse:
        started_at = datetime.now(timezone.utc)
        raw_command = self.build_command(request)
        # Windows argv command length preflight. Run this before the Unicode
        # wrapper is built so blocked calls do not leave temporary scripts.
        if os.name == "nt" and self.spec.prompt_transport != "stdin":
            estimated = self._estimate_windows_command_length(raw_command)
            if estimated > self.spec.max_command_chars:
                sanitized = self._sanitize_command_with_long_prompt(raw_command, request.prompt)
                finished_at = datetime.now(timezone.utc)
                return ProviderResponse(
                    provider=self.spec.name,
                    command=tuple(sanitized),
                    stdout="",
                    stderr=f"Command line would exceed safe Windows length (estimated {estimated} chars > limit {self.spec.max_command_chars}). Configure prompt_transport: stdin or reduce prompt size.",
                    returncode=126,
                    started_at=started_at.isoformat(),
                    finished_at=finished_at.isoformat(),
                    duration_seconds=(finished_at - started_at).total_seconds(),
                    model=request.model or self.spec.default_model,
                    stage=request.stage,
                )
        temp_script: Path | None = None
        if _needs_windows_unicode_wrapper(self.spec, request):
            command, temp_script = _build_windows_unicode_wrapper(self.spec, request)
        else:
            command = raw_command
        timeout = request.timeout_seconds if request.timeout_seconds is not None else self.spec.timeout_seconds
        cwd = request.cwd or self.spec.working_dir
        env = os.environ.copy()
        env.update(self.spec.env)
        env.update(request.env)

        stdin_input = None
        if getattr(self.spec, 'prompt_transport', 'argv') == 'stdin':
            stdin_input = request.prompt
        try:
            subprocess_kwargs = {
                'args': command,
                'cwd': str(cwd) if cwd is not None else None,
                'env': env,
                'capture_output': True,
                'text': True,
                'encoding': 'utf-8',
                'timeout': timeout,
                'check': False,
            }
            if stdin_input is not None:
                subprocess_kwargs['input'] = stdin_input
            completed = subprocess.run(**subprocess_kwargs)
            returncode = int(completed.returncode)
            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            stdout = exc.stdout or ""
            stderr = exc.stderr or f"Timeout after {timeout} seconds."
        except OSError as exc:
            returncode = 127
            stdout = ""
            stderr = str(exc)
        finally:
            if temp_script is not None:
                try:
                    temp_script.unlink(missing_ok=True)
                except OSError:
                    pass

        finished_at = datetime.now(timezone.utc)
        response = ProviderResponse(
            provider=self.spec.name,
            command=tuple(command),
            stdout=stdout,
            stderr=stderr,
            returncode=returncode,
            started_at=started_at.isoformat(),
            finished_at=finished_at.isoformat(),
            duration_seconds=(finished_at - started_at).total_seconds(),
            model=request.model or self.spec.default_model,
            stage=request.stage,
        )
        if check and response.returncode != 0:
            raise ProviderExecutionError(response)
        return response

    def run_with_retry(
        self,
        request: ProviderRequest,
        *,
        require_stdout: bool = True,
        max_attempts: int | None = None,
        retry_delay_seconds: float | None = None,
        retry_backoff_multiplier: float | None = None,
        retry_failure_kinds: tuple[str, ...] | None = None,
        check: bool = False,
        retry_on_nonzero: bool = True,
    ) -> ProviderResponse:
        # Determine effective retry configuration
        effective_max_attempts = max_attempts if max_attempts is not None else self.spec.retry_max_attempts
        effective_initial_delay = retry_delay_seconds if retry_delay_seconds is not None else self.spec.retry_initial_delay_seconds
        effective_backoff_multiplier = retry_backoff_multiplier if retry_backoff_multiplier is not None else self.spec.retry_backoff_multiplier
        effective_failure_kinds = retry_failure_kinds if retry_failure_kinds is not None else self.spec.retry_failure_kinds
        # Incorporate retry_on_nonzero as "nonzero_exit" failure kind
        if retry_on_nonzero and "nonzero_exit" not in effective_failure_kinds:
            effective_failure_kinds = (*effective_failure_kinds, "nonzero_exit")
        # Validation
        if effective_max_attempts < 1:
            raise ValueError(f"max_attempts must be at least 1, got {effective_max_attempts}")
        if effective_initial_delay < 0:
            raise ValueError(f"retry_delay_seconds must be >= 0, got {effective_initial_delay}")
        if effective_backoff_multiplier < 1:
            raise ValueError(f"retry_backoff_multiplier must be >= 1, got {effective_backoff_multiplier}")
        last_response: ProviderResponse | None = None
        for attempt in range(1, effective_max_attempts + 1):
            response = self.run(request, check=False)
            last_response = response
            failure_kind = classify_provider_response(response, require_stdout=require_stdout)
            if not failure_kind:
                if check:
                    return response
                return response
            retryable = failure_kind in effective_failure_kinds
            if attempt < effective_max_attempts and retryable:
                delay = effective_initial_delay * (effective_backoff_multiplier ** (attempt - 1))
                if delay > 0:
                    time.sleep(delay)
                continue
            # No more retries or not retryable
            if check:
                raise ProviderExecutionError(response)
            return response
        # Should not reach here because loop returns or raises, but keep fallback
        if last_response is None:
            raise ProviderExecutionError(
                ProviderResponse(
                    provider=self.spec.name,
                    command=tuple(),
                    stdout="",
                    stderr="No provider response produced.",
                    returncode=1,
                    started_at=datetime.now(timezone.utc).isoformat(),
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_seconds=0.0,
                    model=request.model or self.spec.default_model,
                    stage=request.stage,
                )
            )
        if check and last_response.returncode != 0:
            raise ProviderExecutionError(last_response)
        return last_response


def classify_provider_response(response: ProviderResponse, *, require_stdout: bool = True) -> str:
    """Return a machine-readable failure kind, or an empty string when usable."""
    stdout = response.stdout or ""
    stderr = response.stderr or ""
    combined = f"{stdout}\n{stderr}".strip()
    combined_lower = combined.lower()
    # command_too_long detection
    if response.returncode == 126 and "command line would exceed" in combined_lower:
        return "command_too_long"
    if "the command line is too long" in combined_lower or "command line would exceed" in combined_lower or "argument list too long" in combined_lower:
        return "command_too_long"
    if response.returncode == 124:
        return "timeout"
    if response.returncode == 127:
        return "launch_error"
    if response.returncode != 0:
        for kind, pattern in _FAILURE_PATTERNS:
            if pattern.search(combined):
                return kind
        return "nonzero_exit"
    for kind, pattern in _FAILURE_PATTERNS:
        if pattern.search(combined):
            return kind
    if require_stdout and not stdout.strip():
        return "empty_stdout"
    return ""


def ensure_provider_response(response: ProviderResponse, *, require_stdout: bool = True) -> ProviderResponse:
    failure_kind = classify_provider_response(response, require_stdout=require_stdout)
    if failure_kind:
        preview = (response.stderr or response.stdout or "").strip().replace("\n", " ")[:300]
        raise ProviderOutputError(
            response,
            f"Provider '{response.provider}' returned unusable output ({failure_kind}). {preview}",
        )
    return response


def _needs_windows_unicode_wrapper(spec: ProviderSpec, request: ProviderRequest) -> bool:
    if os.name != "nt":
        return False
    prompt_transport = getattr(spec, 'prompt_transport', 'argv')
    if prompt_transport == 'stdin':
        return False
    if spec.prompt_position == "flag" and not spec.prompt_flag:
        return False
    return any(ord(char) > 127 for char in request.prompt)


def _build_windows_unicode_wrapper(spec: ProviderSpec, request: ProviderRequest) -> tuple[list[str], Path]:
    script_handle = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".ps1",
        prefix="novel_provider_",
        encoding="utf-8-sig",
        delete=False,
    )
    script_path = Path(script_handle.name)
    try:
        script_handle.write("$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()\n")
        script_handle.write("$prompt = @'\n")
        script_handle.write(request.prompt.replace("\n'@", "\n' @"))
        script_handle.write("\n'@\n")
        script_handle.write("& ")
        script_args = [*spec.executable, *spec.extra_args, *request.extra_args]
        for arg in script_args:
            script_handle.write(_powershell_quote(arg))
            script_handle.write(" ")
        model = request.model or spec.default_model
        if model and spec.model_position == "before_prompt" and spec.model_flag:
            script_handle.write(str(spec.model_flag))
            script_handle.write(" ")
            script_handle.write(_powershell_quote(model))
            script_handle.write(" ")
        if spec.prompt_position == "flag":
            script_handle.write(str(spec.prompt_flag))
            script_handle.write(" $prompt")
        elif spec.prompt_position == "positional":
            script_handle.write("$prompt")
        else:
            raise ValueError(f"Unsupported prompt_position '{spec.prompt_position}' for provider '{spec.name}'.")
        if model and spec.model_position != "before_prompt" and spec.model_flag:
            script_handle.write(" ")
            script_handle.write(str(spec.model_flag))
            script_handle.write(" ")
            script_handle.write(_powershell_quote(model))
        script_handle.write("\nexit $LASTEXITCODE\n")
    finally:
        script_handle.close()

    return (
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
        ],
        script_path,
    )


def _powershell_quote(value: object) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def runner_for_provider(name: str, *, data: Mapping[str, Any] | None = None, base_dir: Path | None = None) -> ProviderRunner:
    return ProviderRunner(build_provider_spec(name, data, base_dir=base_dir))


__all__ = [
    "ProviderExecutionError",
    "ProviderOutputError",
    "ProviderRunner",
    "build_provider_spec",
    "classify_provider_response",
    "default_provider_specs",
    "ensure_provider_response",
    "runner_for_provider",
]
