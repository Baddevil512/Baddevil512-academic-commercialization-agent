"""Offline common Reviewer contract; no model import, client or execution path.

The caller owns both inputs and supplies the actual local model's complete
JSON Schema. This only prepares new request bytes. It neither changes the
validator nor repairs a response from a closed experiment.
"""

from __future__ import annotations

import json
import math


MAX_REQUEST_BYTES = 48 * 1024
CONTRACT_MARKER = "\n\nShared Reviewer output contract v1:\n"


class ContractError(ValueError):
    """A fixed preparation category, without input text in diagnostics."""


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate_json_key")
        result[key] = value
    return result


def _nonfinite(_value: str) -> None:
    raise ContractError("nonfinite_json")


def _json_value(value: object) -> None:
    # json.dumps silently turns integer keys into strings and tuples into
    # lists. Reject those conversions: the trusted schema must retain its
    # complete JSON values, not a best-effort normalization of arbitrary code.
    if type(value) in (str, bool, int, type(None)):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for item in value:
            _json_value(item)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values():
            _json_value(item)
        return
    raise ContractError("invalid_json_value")


def _wire(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def append_common_contract(
    request_body: bytes, *, trusted_schema: dict[str, object],
) -> bytes:
    """Append an identical complete contract to one trusted system message.

    Supports the two-text-message JSON Object request used by the direct
    comparison. Unknown shapes are refused rather than silently reordered.
    Original JSON values and message strings survive; whitespace, key order
    and escaping may be canonicalized. The returned bytes need a new identity.

    The caller must provide ReviewerCorrectionPlan.model_json_schema() from
    its trusted validator. Structural checks here do not authenticate a schema
    or prove that a provider will follow it. This function has no dispatcher.
    """

    if type(request_body) is not bytes or len(request_body) > MAX_REQUEST_BYTES:
        raise ContractError("request_byte_bound_or_type")
    try:
        body = json.loads(request_body.decode("utf-8"), object_pairs_hook=_object,
                          parse_constant=_nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise ContractError("invalid_request_json") from None
    if type(body) is not dict or body.get("response_format") != {"type": "json_object"}:
        raise ContractError("unsupported_request_shape")
    messages = body.get("messages")
    if (type(messages) is not list or len(messages) != 2
            or any(type(message) is not dict for message in messages)
            or [message.get("role") for message in messages] != ["system", "user"]
            or any(type(message.get("content")) is not str for message in messages)):
        raise ContractError("unsupported_message_shape")
    if CONTRACT_MARKER in messages[0]["content"]:
        raise ContractError("contract_already_present")
    if (type(trusted_schema) is not dict or trusted_schema.get("type") != "object"
            or type(trusted_schema.get("properties")) is not dict
            or "corrections" not in trusted_schema["properties"]):
        raise ContractError("unsupported_schema_shape")
    try:
        _json_value(trusted_schema)
        common = {
            "output": "Return one JSON object without Markdown fences or surrounding prose.",
            # The local model defaults an omitted array to []. State the task's
            # explicit envelope separately; do not pretend its schema requires
            # the field or modify the production model to make that claim true.
            "required_top_level_fields": ["corrections"],
            "length_limits": (
                "minLength and maxLength include their endpoints and count Unicode code points. "
                "Use these precise schema limits if older prose says 'under 2,000'."
            ),
            "json_schema": trusted_schema,
        }
        messages[0]["content"] += CONTRACT_MARKER + _wire(common).decode("utf-8")
        rendered = _wire(body)
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise ContractError("invalid_schema_json") from None
    # Count the entire serialized UTF-8 request after appending. Checking only
    # characters or the pre-append body would miss this added admission cost.
    if len(rendered) > MAX_REQUEST_BYTES:
        raise ContractError("request_byte_bound")
    return rendered
