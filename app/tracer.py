from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_LOG_FILE = LOGS_DIR / "agent_traces.jsonl"


class AgentTracer:
    """Structured tracer for multi-agent interactions conforming to Hackathon Trace Requirements."""

    def __init__(self, log_file: Path | str | None = None, echo_stdout: bool = True):
        self.log_file = Path(log_file) if log_file else DEFAULT_LOG_FILE
        self.echo_stdout = echo_stdout
        self.session_traces: list[dict[str, Any]] = []

    def log_event(
        self,
        agent_name: str,
        action: str,
        input_summary: str,
        output_summary: str,
        target_agent: Optional[str] = None,
        model: str = "nvidia/nemotron-3-super-120b-a12b",
        confidence: float = 0.95,
        retry_count: int = 0,
        status: str = "success",
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Record a single step in multi-agent reasoning trajectory."""
        entry: dict[str, Any] = {
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "agent_name": agent_name,
            "action": action,
            "input_summary": input_summary[:500],
            "output_summary": output_summary[:500],
            "target_agent": target_agent,
            "model": model,
            "confidence": round(float(confidence), 2),
            "retry_count": int(retry_count),
            "status": status,
        }
        if metadata:
            entry["metadata"] = metadata

        self.session_traces.append(entry)

        # Write to JSONL file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:
            print(f"[Tracer Error writing to {self.log_file}]: {exc}", file=sys.stderr)

        # Echo formatted message to stdout
        if self.echo_stdout:
            target_str = f" -> {target_agent}" if target_agent else ""
            status_indicator = "✓" if status == "success" else ("⚠" if status == "needs_revision" else "✗")
            print(
                f"[TRACE] {status_indicator} [{entry['timestamp']}] {agent_name}{target_str} "
                f"({action}) | {input_summary[:60]}... => {output_summary[:60]}... "
                f"[{model} conf={confidence:.2f} retry={retry_count}]"
            )

        return entry

    def get_traces(self) -> list[dict[str, Any]]:
        return list(self.session_traces)

    def clear(self) -> None:
        self.session_traces.clear()

