# J-tau: A Japanese tau-bench for Benchmarking Tool-Agent-User Interaction in Real-World Domains

[![日本語 README](https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-red)](README.md)
[![Tech Blog(Japanese)](<https://img.shields.io/badge/Blog_(Japanese)-telecom_ja-orange>)](https://www.sbintuitions.co.jp/blog/entry/2026/06/19/100154)

## Overview

J-tau is a benchmark for evaluating agent capabilities in Japanese.
It measures accuracy in tool use and user interaction according to defined policies in customer service scenarios.

This repository is a Japanese version based on [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench), and currently supports evaluation only for `telecom_ja`, `airline_ja` and `retail_ja`. For evaluating other English domains, please use the original repository.

## Supported Domains

### telecom_ja

A domain based on customer support for telecommunications services. The agent must access user information and instruct users to operate their own devices.

### airline_ja

A domain based on customer support for airline services. The agent must access user reservation information and handle flight changes, cancellations, refunds, and more according to defined policies.

### retail_ja

A domain based on customer support for a retail business. The agent must verify the user's identity, then handle order cancellations/modifications, returns/exchanges, and address changes according to the policy.

For `retail_ja` and `airline_ja`, we also modified some task content in addition to translation. See [TASK_CHANGES_EN.md](TASK_CHANGES_EN.md) for details.

## Quickstart

### 1. Installation

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/sbintuitions/j-tau-bench.git
cd j-tau-bench
uv sync
```

### 2. Set API Keys

Various providers are supported via [LiteLLM](https://docs.litellm.ai/docs/providers).

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 3. Run Evaluation

```bash
uv run tau2 run \
  --domain telecom_ja \
  --agent-llm <llm_name> \
  --user-llm <llm_name> \
  --num-trials 1
```

| Argument | Description |
|----------|-------------|
| `--agent-llm` | LLM for the agent (specified in [LiteLLM format](https://docs.litellm.ai/docs/providers)) |
| `--agent-llm-args` | Additional arguments for the agent LLM (JSON). Can include `api_base`, etc. |
| `--user-llm` | LLM for the user simulator |
| `--user-llm-args` | Additional arguments for the user simulator LLM (JSON) |
| `--num-trials` | Number of trials per task |
| `--num-tasks` | Number of tasks to run |

To evaluate a model served with vLLM, specify the model name and `api_base` following the LiteLLM format:

```bash
uv run tau2 run \
  --domain telecom_ja \
  --agent-llm hosted_vllm/<agent_model_name> \
  --agent-llm-args '{"api_base": <agent_api_base>}' \
  --user-llm hosted_vllm/<user_model_name> \
  --user-llm-args '{"api_base": <user_api_base>}' \
  --num-trials 1
```

Results are saved to `data/simulations/` and can be viewed with `uv run tau2 view`.

### NL Assertions Evaluation (retail_ja domain)

Some tasks in the `retail_ja` domain judge part of the reward using an LLM to evaluate the conversation content. This evaluation is not used in other domains.

By default, it uses the `gpt-oss-120b` model served by a vLLM server running at `http://localhost:8000/v1`.
Following the LiteLLM format, you can specify the model name and `api_base` as follows:

```bash
export TAU2_NL_ASSERTIONS_MODEL=hosted_vllm/<nl_assertion_model_name> TAU2_NL_ASSERTIONS_API_BASE=http://<host>:<port>/v1
```

If you specify a hosted API model as follows, `TAU2_NL_ASSERTIONS_API_BASE` is not needed.

```bash
export TAU2_NL_ASSERTIONS_MODEL=gpt-5-mini-2025-08-07
```

| Environment Variable | Description |
|----------|-------------|
| `TAU2_NL_ASSERTIONS_MODEL` | Model name used for the nl_assertions evaluation |
| `TAU2_NL_ASSERTIONS_API_BASE` | Server URL when using a locally hosted model |

## Comparing with the original tau2-bench

Besides adding Japanese domains, J-tau also makes fixes to the evaluation framework itself,
such as a revised error classification scheme and enabling Anthropic prompt caching for Claude.

If you want to evaluate the English domains with the same fixes applied, apply the patches under
[patches/](patches/) to the original repository before running it. See
[patches/README_EN.md](patches/README_EN.md) for details on what each patch changes.
Note that some tasks in the `airline` and `retail` domains have also been corrected, so results
from J-tau and the original tau-bench are not directly comparable even with the patches applied
(see [TASK_CHANGES_EN.md](TASK_CHANGES_EN.md) for details).

```bash
bash patches/apply.sh   # -> generates a patched copy of the repo at ./tau2-bench-patched/
```

## License

[Modified MIT License](LICENSE)

## Acknowledgements

We thank the [tau-bench](https://github.com/sierra-research/tau2-bench) project for providing an excellent evaluation framework.
tau-bench is released under the [MIT License](https://github.com/sierra-research/tau-bench/blob/main/LICENSE).

## Citation

```
@misc{j-tau-2026,
  author       = {Chihiro, Yano and Jun, Hirako and Ryota, Hirobuchi},
  title    = {J-tau: A Japanese tau-bench for Benchmarking　Tool-Agent-User Interaction in Real-World Domains},
  url = {https://github.com/sbintuitions/j-tau-bench},
  howpublished = {\url{https://github.com/sbintuitions/j-tau-bench}},
  year     = {2026},
  version  = {v202606}
}
```
