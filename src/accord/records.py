"""Read and validate Accord's append-only schema-1 records."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any


TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
TERMINAL_TYPES = {"completion", "end"}
NEW_EVENT_ACTORS = {"human", "agent", "supporting-agent"}


class RecordError(Exception):
    """A record cannot be trusted or safely changed."""


@dataclass(frozen=True)
class Record:
    """A parsed record and the bytes from which it was read."""

    path: Path
    events: list[dict[str, Any]]
    raw: bytes

    @property
    def last_event(self) -> dict[str, Any] | None:
        return self.events[-1] if self.events else None

    @property
    def closed(self) -> bool:
        return bool(self.last_event and self.last_event.get("type") in TERMINAL_TYPES)


def load_schema() -> dict[str, Any]:
    """Load the schema shipped inside the standalone package."""
    resource = files("accord").joinpath("resources/record.schema.json")
    try:
        with resource.open("r", encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise RecordError(f"cannot load the bundled record schema: {error}") from error

    try:
        conditionals = {
            clause["if"]["properties"]["type"]["const"]: clause["then"]["required"]
            for clause in schema.get("allOf", [])
        }
        conditional_fields = {
            field for required in conditionals.values() for field in required
        }
        return {
            "required": schema["required"],
            "properties": schema["properties"],
            "conditionals": conditionals,
            "conditional_fields": conditional_fields,
        }
    except (KeyError, TypeError) as error:
        raise RecordError(f"bundled record schema is incomplete: {error}") from error


def check_value(name: str, specification: dict[str, Any], value: object) -> str | None:
    """Validate a value against the small JSON Schema subset Accord uses."""
    if "const" in specification:
        if value != specification["const"]:
            return f"{name} must be {specification['const']!r}, got {value!r}"
        return None
    if "enum" in specification:
        if value not in specification["enum"]:
            return f"{name} must be one of {specification['enum']}, got {value!r}"
        return None

    value_type = specification.get("type")
    if value_type == "string":
        if not isinstance(value, str):
            return f"{name} must be a string"
        if len(value) < specification.get("minLength", 0):
            return f"{name} must be non-empty"
        if specification.get("format") == "date-time" and not TS_RE.match(value):
            return f"{name} is not an ISO 8601 date-time: {value!r}"
    elif value_type == "array":
        if not isinstance(value, list):
            return f"{name} must be an array"
        for index, item in enumerate(value):
            error = check_value(f"{name}[{index}]", specification["items"], item)
            if error:
                return error
    return None


def validate_event(event: object, schema: dict[str, Any] | None = None) -> list[str]:
    """Return every structural error in one event."""
    if not isinstance(event, dict):
        return ["line is not a JSON object"]
    active_schema = schema or load_schema()
    errors: list[str] = []

    for field in active_schema["required"]:
        if field not in event:
            errors.append(f"missing required field {field!r}")

    for field, value in event.items():
        if field not in active_schema["properties"]:
            errors.append(f"unknown field {field!r}")
            continue
        error = check_value(field, active_schema["properties"][field], value)
        if error:
            errors.append(error)

    event_type = event.get("type")
    if isinstance(event_type, str):
        required = active_schema["conditionals"].get(event_type, [])
        for field in required:
            if field not in event:
                errors.append(f"type {event_type!r} requires field {field!r}")
        for field in active_schema["conditional_fields"]:
            if field in event and field not in required:
                errors.append(f"field {field!r} is not allowed on type {event_type!r}")
    return errors


def parse_record_bytes(path: Path, raw: bytes) -> Record:
    """Parse and validate a record without altering it."""
    schema = load_schema()
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RecordError(f"{path}: record is not UTF-8: {error}") from error

    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"line {line_number}: invalid JSON: {error}")
            continue
        line_errors = validate_event(event, schema)
        errors.extend(f"line {line_number}: {error}" for error in line_errors)
        if isinstance(event, dict):
            events.append(event)

    if not events and not errors:
        errors.append("record is empty")
    if errors:
        raise RecordError(f"{path}: " + "; ".join(errors))
    return Record(path=path, events=events, raw=raw)


def read_record(path: Path, expected_task: str | None = None) -> Record:
    """Read a valid record and optionally require its task identity."""
    if path.is_symlink():
        raise RecordError(f"{path}: record.jsonl is a symlink")
    if not path.is_file():
        raise RecordError(f"{path}: record.jsonl is not a regular file")
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise RecordError(f"{path}: cannot read record: {error}") from error
    record = parse_record_bytes(path, raw)
    if expected_task and any(
        event.get("task") != expected_task for event in record.events
    ):
        raise RecordError(f"{path}: record events do not name {expected_task!r}")
    return record
