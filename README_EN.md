# J-tau: A Japanese tau-bench for Benchmarking Tool-Agent-User Interaction in Real-World Domains

[![日本語 README](https://img.shields.io/badge/README-%E6%97%A5%E6%9C%AC%E8%AA%9E-red)](README.md)

## Overview

J-tau is a benchmark for evaluating agent capabilities in Japanese.
It measures accuracy in tool use and user interaction according to defined policies in customer service scenarios.

This repository is a Japanese version based on [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench), and currently supports evaluation only for `telecom_ja`. For evaluating other English domains, please use the original repository.

## Supported Domains

### telecom_ja
A domain based on customer support for telecommunications services. The agent must access user information and instruct users to operate their own devices.

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
