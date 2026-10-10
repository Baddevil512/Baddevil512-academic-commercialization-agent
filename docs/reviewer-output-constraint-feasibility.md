# Reviewer output constraints: offline feasibility review

Reviewed 2026-10-10 (Australia/Sydney). Scope: public documentation, the frozen
request/schema, existing test contracts and qualified closeout records. No new
provider call, credential read, response repair or experiment execution occurred.
No successor model, endpoint, runner, cohort or allowance is selected here.

The [closed v3 result](results-2026-10-10-reviewer-comparison-v3.md) establishes
one concrete gap: the prompt transmitted a 300-code-point reason limit, yet the
response contained 378. Its JSON was valid and the local validator correctly
rejected it. Prompt/schema presence, provider enforcement and useful corrections
are separate observations.

## Public API evidence

The official [structured-output guide](https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output)
was reviewed alongside the [OpenAI-compatible API reference](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions).
The guide was updated September 28, 2026. These are current documentation
observations, not a native compatibility test or a promise about later versions.

| Question | Evidence classification | Consequence for this project |
| --- | --- | --- |
| `qwen3.5-plus`, non-thinking, `json_object` | Documented; JSON validity, not fixed structure | Retain local validation |
| `qwen3.5-plus` with `json_schema` | Not listed in the current Schema model list | No automatic format switch |
| Strict Schema mode | Structure/types documented for listed Qwen3.7 Plus/Flash/Max and Qwen3.8 Max/Flash families | A named candidate still needs exact compatibility evidence |
| `maxLength`, `minLength`, `maxItems` | Not explicitly specified in the reviewed API references | Length/list enforcement is unestablished |
| `$defs`, `$ref` | Not explicitly specified | Do not assume the complete local schema is accepted |
| `properties`, `required`, `additionalProperties`; basic types and `enum` | Documented API constructs | This does not prove every schema keyword works |
| Unknown keywords or unsupported combinations | Rejection/ignore/downgrade behavior unspecified | Treat the outcome as unknown |
| Singapore Schema support | Guide says unavailable; examples use Singapore URLs | Conflicting documentation, unresolved |
| Multimodal Schema requests | Guide documents fallback to JSON Object | Any future diagnostic should isolate text-only behavior |
| Existing legacy endpoint vs documented workspace-specific examples | The exact new mode/endpoint combination is untested | Do not silently migrate the endpoint |

The local conclusion is therefore **provider length enforcement unestablished**,
not "JSON Schema unsupported everywhere" or "strict mode guarantees 300".
The documentation's broad structured-output badge is insufficient to establish
the needed model/region/keyword combination.

## Frozen local requirements and existing checks

The source-locked Pydantic schema contains a referenced correction definition,
three required string fields and no additional fields. Reason length is 3..300,
find length is 1..2000, replacement length is 0..2000, and the array permits at
most 20 corrections. Bounds count Unicode code points, not bytes or tokens.
The model defaults an omitted corrections array; v3's explicit wire contract
separately requires that envelope. Any future adapter must preserve both facts
without falsely describing the Pydantic field as schema-required.

These existing checks already belonged to the 35 common-contract checks within
each successful 529-check preparation cell:

- `tests/reviewer_output_contract_checks.py::test_real_validator_string_boundaries`
  covers reason lengths 2, 3, 300, 301, 313 and 359 with non-ASCII characters,
  alongside find/replacement boundaries.
- `test_real_validator_correction_count` covers 20/21 items;
  `test_real_validator_types_and_extra_fields` rejects extra fields and a
  non-string reason.
- `test_complete_common_schema_reaches_both_http_bodies` checks full schema
  delivery through intercepted HTTP bytes. It is not provider enforcement.

This review reuses that recorded coverage; it does not report a fresh run of
those tests. Their real-production-model import needs the established isolation
path, so a standalone pytest shortcut is not used. No duplicate boundary tests,
new skip, warning ignore or full-suite invocation is introduced for this review.

The offline audit checks the frozen manifest/schema and source bindings only.
It does not execute the runner or revalidate/repair the occupied native output.
Reducing a whole-response token cap is not a reason-field character constraint:
the failed response used only 160 output tokens. The existing output/byte/time
bounds remain necessary and must not be removed to follow a vendor example.

## Smallest justified next step

1. Name one documented model, region and exact endpoint, and enumerate every
   schema keyword needed by a new isolated contract. Record unsupported or
   uncertain features explicitly; do not alter the frozen v3 artifacts.
2. Specify a few fresh synthetic contract controls, including a compliant value,
   pressure to exceed the field bound, and Unicode counting. Declare success,
   failure, refusal, ignored constraints and unavailable observations separately.
   Local parsing or a mocked response cannot settle provider behavior.
3. Only after separate review and explicit new authorization, run a small new
   native contract check. A conforming answer alone is not proof of universal
   decoder enforcement. Preserve local validation and first-fault closure.

Only observed compatibility justifies considering a new paired Reviewer study.
If its model changes, both arms must use the same new model under a distinct
method identity; it cannot retrospectively repair v3 or isolate model changes
from earlier experiments. No production change or additional paid request is
authorized by this document.
