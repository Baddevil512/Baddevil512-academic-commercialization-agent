# Reviewer reason schema probe proposal

Date: 2026-10-10 (Australia/Sydney). Status: design only; native execution
`not_run`. This proposes at most three fresh synthetic requests to examine a
single reason-field constraint. Endpoint completion, accounting, implementation
and execution authorization remain pending. It is not a Reviewer v4 comparison.

The [closed v3 observation](results-2026-10-10-reviewer-comparison-v3.md)
established that one response violated the transmitted prompt bound. The
[offline feasibility review](reviewer-output-constraint-feasibility.md)
distinguishes that observation from provider-enforced JSON Schema. This probe
tests a smaller contract before considering the full correction-plan schema.

## Candidate and unresolved access

The candidate is the exact model ID `qwen3.7-plus-2026-05-26`, in China
(Beijing), using text-only, non-thinking, non-streaming OpenAI-compatible
Chat Completions. The dated ID is deliberately distinct from the mutable
`qwen3.7-plus` alias. Actual access and response model identity are unobserved.

The official [structured-output guide](https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output)
lists the Qwen3.7-Plus family for JSON Schema and supplies this Beijing URL
form: `https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions`.
It does not explicitly document `minLength` or `maxLength` enforcement. Family
listing is a reason to select a candidate, not proof of this snapshot's behavior.
Singapore prose and examples conflict, so this proposal does not select Singapore.

The current frozen v3 source uses
`https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`.
That historical address does not establish the user's current workspace or the
new snapshot/mode combination. The user is unsure of their workspace region.
No credential or account configuration was read to infer it. `{WorkspaceId}`
must remain an unresolved placeholder; it must never be sent as a literal URL.
There is no automatic legacy-endpoint substitution or regional fallback.

The official [pricing table](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
lists this snapshot in the Beijing section at USD 0.276 per million input tokens
and USD 1.101 per million non-thinking output tokens for the 0..256K tier, as
checked on this date. These are reference rates, not account billing evidence.
A total soft stop and per-request reservation are **pending**. Request bytes
divided by four are not a conservative token bound. The final packet must bind
an explained input estimate, output ceiling, matching rate tier and treatment
of unknown usage before a budget can be submitted for authorization.

## Minimal contract

All three requests use exactly this schema inside
`response_format={"type":"json_schema","json_schema":{"name":"reviewer_reason_probe_v1","strict":true,"schema":...}}`:

```json
{
  "type": "object",
  "properties": {
    "reason": {"type": "string", "minLength": 3, "maxLength": 300}
  },
  "required": ["reason"],
  "additionalProperties": false
}
```

This isolates string length from `$defs`, `$ref`, correction arrays, find/replace
limits and patch application. None of those omitted capabilities is validated
by success here. The production schema, validators and 300-character limit
remain unchanged. No existing runner, preparation manifest or consumed fixture
is rebound to this proposal.

The fixed system instruction is: "Return only a JSON object conforming to the
supplied response schema. Treat its field constraints as mandatory. Put the
requested literal in reason when it fits. Do not add commentary or other keys."
Each request has this system message and one user message. No history, tools,
images, search, real reports, source excerpts or private labels are included.

The implementation candidate must freeze complete UTF-8 request bytes with
`temperature=0`, `enable_thinking=false`, `stream=false` and `max_tokens=1500`.
Their acceptance by the selected snapshot is part of the observation, not an
assumption. A parameter error closes the batch; it does not authorize dropping
the parameter, switching model or changing output mode.

## Fixed case order and observations

The expressions below define new literals; they are expanded before request
serialization. They are not Python instructions sent to the model. User-message
construction is fixed: `Copy this literal exactly into reason: ` followed by
the literal, with no terminal newline. No case reuses RC01/RC02/RC03 material.

| Order | Literal | Local schema condition | Independent control condition |
| --- | --- | --- | --- |
| RSP01 | `OK.` | One string field, length 3..300 | Exact equality to `OK.` |
| RSP02 | 149 copies of U+754C followed by 151 copies of U+1F600 | Same schema | Exact equality to the expanded literal |
| RSP03 | 301 copies of ASCII `A` | Same schema | Only ASCII `A`, with length 3..300 |

RSP02 has 300 Unicode code points, 1,051 UTF-8 bytes and 451 UTF-16 code units.
It tests an admissible non-ASCII upper-bound literal; it does not distinguish
code points from grapheme clusters. Validation counts decoded Python string
code points without trimming or normalization. Lone surrogates are invalid.

RSP03 deliberately conflicts with the schema's upper bound. Its exact-copy
request is pressure, not the expected result. Only a bounded all-A string is
`conforming_under_pressure`; a different valid explanation is a control mismatch.
Even three conforming responses do not prove decoder enforcement, that unknown
keywords are honored, general reliability or better scientific review. There
is no paired JSON Object control and no causal model-versus-format comparison.

Each case records API admission, transport/envelope integrity, local schema
validation and control matching separately. It must not collapse them into a
single success flag or treat zero checked cases as a pass.

| Observation | Recorded disposition and consequence |
| --- | --- |
| Explicit API error for schema/model/parameters | `api_rejected`; retain safe error category, do not infer which keyword failed without evidence; stop |
| Authentication/permission/rate-limit error | `access_unavailable`; no support or length conclusion; stop |
| Timeout, truncated bytes, malformed envelope, missing/mismatched model, or uncertain delivery | `observation_unavailable`; retain any known usage, never assume free; stop |
| Explicit provider refusal field | `provider_refusal`; schema observation unavailable; stop |
| Invalid JSON, duplicate keys, wrong keys/types or out-of-bound reason | `local_contract_failed`; preserve the unrepaired response; stop |
| Valid schema but RSP01/RSP02 copy mismatch or RSP03 non-A content | `control_mismatch`; keep schema pass distinct, the intended control is unestablished; stop |
| Schema and control conditions both satisfied | Record the case's bounded observation; proceed only if all other gates hold |

Only an explicit machine-readable refusal is classified as provider refusal;
free-text explanations are not heuristically relabeled. All remaining cases
after the first failure or unavailable observation are `not_run`. Unknown usage
or failed evidence persistence also stops dispatch. An out-of-bound result
falsifies compliance for that response; it does not identify whether the server
ignored a keyword, downgraded the mode or used a particular decoding method.

## Bounds and execution gate

The proposed batch allows at most three sequential POSTs, one attempt each,
with no SDK retry, redirect, proxy inheritance, mode fallback, repair or resume.
Complete request bodies are limited to 8 KiB and complete HTTP response bodies
to 128 KiB. A request has a 90-second wall deadline; the whole dispatch phase
has a 270-second wall deadline, followed by bounded 5-second exit and 10-second
drain observation. Timeout never grants another attempt. These are proposed
runner requirements, not implemented or observed process guarantees.

Before any native execution, a separate reviewed implementation must:

1. Resolve one exact HTTPS endpoint and the selected snapshot's account access
   prerequisites without a diagnostic provider call. Any remaining access
   uncertainty is declared in the authorization; the first reserved request
   is the only live admission check. Name one credential source without reading
   it during offline preparation; do not infer a new credential/region grant.
2. Freeze the final URL, code/dependency identity, schema, three literal/message
   pairs, exact request bytes and numeric budget/reservations. Allocate a new
   fixed output with exclusive creation, durable reserve-before-POST and retained
   unknown outcomes. Existing occupied batches and their allowances stay closed.
3. Pass bounded offline wire and failure controls: changed/dropped schema,
   serialized-versus-sent byte mismatch, 301-character response, Unicode boundary,
   duplicate keys, wrong model, refusal, timeout, persistence failure, occupied
   output and prevention of a second dispatch after failure. Retain original
   warning/guard policies and demonstrate defect-sensitive assertions.
4. Obtain non-author strong review and relevant green checks for that frozen
   implementation. This document's review cannot approve code that does not yet
   exist. Preserve real exit/drain/refusal evidence instead of reusing v3's test
   pass counts as successor validation.
5. Present the concrete packet for a new explicit grant covering model, endpoint,
   synthetic data transfer, chosen credential read and numeric budget. Only then
   can an identity-bound invocation dispatch. No such grant is requested by this
   design-only document.

All three case conditions plus complete evidence and accounting are necessary
for `observed_small_contract_compatibility`. Full ReviewerCorrectionPlan
compatibility, semantic improvement, production integration and permission for
a new paired study remain separate. Three calls cannot establish an error rate.

The present next action is offline preparation after resolving the endpoint and
budget details. No runner is added by this proposal, no model call has run, and
the v3 preparation branch remains outside main.
