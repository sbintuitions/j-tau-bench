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

### 1. Orchestrator error-handling fix (`0001-orchestrator-error-classification.patch`)

- **Target file**: `src/tau2/orchestrator/orchestrator.py`

In tau-bench, some errors were classified as `INFRASTRUCTURE_ERROR`, retried, and then excluded
from the score aggregation — even when the failure was clearly the model's own fault. This patch
reclassifies those cases correctly.
Specifically, the following are now classified as a participant (speaker) failure and scored as 0:

- An empty output (no content and no tool_calls) with `finish_reason` of `stop` or `content_filter`
- Corrupted JSON in tool call arguments (`json.JSONDecodeError`)

### 2. Enable Claude prompt caching (`0002-claude-prompt-cache.patch`)

- **Target file**: `src/tau2/utils/llm_utils.py`

To reduce API cost, this adds the `cache_control: {type: ephemeral}` field to the system message
and tools schema at generation time, enabling Anthropic Claude's automatic prompt caching.

## How to apply

```sh
bash patches/apply.sh                       # -> ./tau2-bench-patched/
# or specify a target directory name
bash patches/apply.sh my-tau2               # -> ./my-tau2/
```
