# tau2-bench compatibility patches

[![日本語 README](https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-red)](README.md)

J-tau is a fork of `sierra-research/tau2-bench` with Japanese domains added, but it also
includes fixes to the evaluation framework itself.

This directory carries that diff as a patch against a
[specific commit](https://github.com/sierra-research/tau2-bench/commit/f0927a4b9cdfa7b374269efaa29ff7fdac90d8fc)
of [`sierra-research/tau2-bench`](https://github.com/sierra-research/tau2-bench).
Applying these patches when evaluating the English domains with the original implementation lets
you run the same evaluation framework as J-tau.
Note, however, that some tasks in the `airline` and `retail` domains have also been corrected, so
even with the patches applied, results from J-tau and tau-bench are not directly comparable.

## What's in the patches

| File | Description |
|---|---|
| [`0001-orchestrator-error-classification.patch`](0001-orchestrator-error-classification.patch) | Orchestrator error-handling fix |
| [`0002-claude-prompt-cache.patch`](0002-claude-prompt-cache.patch) | Enables Claude prompt caching |
| [`0003-exclude-user-error-from-metrics.patch`](0003-exclude-user-error-from-metrics.patch) | Excludes `USER_ERROR` from metrics and retries it |
| [`0004-nl-assertions-config.patch`](0004-nl-assertions-config.patch) | Makes the NL Assertions evaluation model/api_base configurable via env vars |
| [`0005-user-review-critical-severity.patch`](0005-user-review-critical-severity.patch) | Fixes critical user errors being dropped by the user-mode review judge |

### 1. Orchestrator error-handling fix (`0001-orchestrator-error-classification.patch`)

- **Target file**: `src/tau2/orchestrator/orchestrator.py`

In tau-bench, some errors were classified as `INFRASTRUCTURE_ERROR`, retried, and then excluded
from the score aggregation — even when the failure was clearly the model's own fault. This patch
reclassifies those cases correctly.
Specifically, the following are now classified as a participant (speaker) failure and scored as 0:

- An empty output (no content and no tool_calls) with `finish_reason` of `stop`, `content_filter`, or `length`
- Corrupted JSON in tool call arguments (`json.JSONDecodeError`)

Conversely, when `finish_reason` cannot be obtained (`None`) or holds an unknown value, there is no
basis for blaming the speaker, so the run is retried and treated as an `INFRASTRUCTURE_ERROR`.
Scoring an undiagnosable failure as the speaker's fault would let serving-side anomalies leak
straight into the score.

The patch also records the cause of `AGENT_ERROR` / `USER_ERROR` terminations (the exception message
and `finish_reason`) in `SimulationRun.info`. The offending message is not part of the trajectory, so
without this the cause cannot be identified after the fact.

### 2. Enable Claude prompt caching (`0002-claude-prompt-cache.patch`)

- **Target file**: `src/tau2/utils/llm_utils.py`

To reduce API cost, this adds the `cache_control: {type: ephemeral}` field to the system message
and tools schema at generation time, enabling Anthropic Claude's automatic prompt caching.

### 3. Exclude `USER_ERROR` from metrics (`0003-exclude-user-error-from-metrics.patch`)

- **Target files**: `src/tau2/data_model/simulation.py`, `src/tau2/metrics/agent_metrics.py`, `src/tau2/runner/checkpoint.py`, `src/tau2/utils/display.py`, `src/tau2/scripts/view_simulations.py`

A `USER_ERROR` means the run was cut short by bad output from the user simulator, which cannot be
attributed to the agent. It is therefore treated the same way as `INFRASTRUCTURE_ERROR`.

- Defines `EXCLUDED_TERMINATION_REASONS` (`INFRASTRUCTURE_ERROR` and `USER_ERROR`) and drops them from the metrics denominator
- Retries them when resuming from a checkpoint (leaving them excluded would starve the trial count and make `pass^k` uncomputable)
- Distinguishes scored failures (`AGENT_ERROR`) from excluded ones (`USER_ERROR` / `INFRASTRUCTURE_ERROR`) with separate colors and icons in the viewer and summary output

### 4. Configurable NL Assertions model/api_base (`0004-nl-assertions-config.patch`)

- **Target file**: `src/tau2/config.py`

Upstream's `retail` domain also has tasks that use `nl_assertions` (LLM-based judging of the
conversation), but the default model was hard-coded. This patch makes it overridable via env vars.

Note that this changes the default to `hosted_vllm/gpt-oss-120b` (a local vLLM server on
`http://localhost:8000/v1`), the same as J-tau — not upstream's original default of
`gpt-4.1-2025-04-14` (a hosted API, no local server needed). To keep using upstream's original
default, set the env var explicitly:

```bash
export TAU2_NL_ASSERTIONS_MODEL=gpt-4.1-2025-04-14
```

| Environment Variable | Description |
|----------|-------------|
| `TAU2_NL_ASSERTIONS_MODEL` | Model name used for the nl_assertions evaluation |
| `TAU2_NL_ASSERTIONS_API_BASE` | Server URL when using a locally hosted model |

### 5. Fix critical user errors being dropped by the user-mode review judge (`0005-user-review-critical-severity.patch`)

- **Target file**: `src/tau2/data_model/simulation.py`

The LLM judge in `review_llm_judge_user_only.py` returns `severity` as one of `"minor"`, `"critical_helped"`,
or `"critical_hindered"`, but the Pydantic schema for `UserOnlyReviewError.severity` that stores it was still
`Literal["minor", "critical"]`. As a result, every time the judge returned `critical_helped` or
`critical_hindered`, constructing `UserOnlyReviewError` raised a validation error and that critical user
error was silently lost. This patch aligns the schema to
`Literal["minor", "critical_helped", "critical_hindered"]`.

## How to apply

```sh
bash patches/apply.sh                       # -> ./tau2-bench-patched/
# or specify a target directory name
bash patches/apply.sh my-tau2               # -> ./my-tau2/
```
