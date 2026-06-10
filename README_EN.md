# J-tau: A Japanese tau-bench for Benchmarking Tool-Agent-User Interaction in Real-World Domains

J-tau is a benchmark specialized for evaluating agent capabilities in Japanese.

## Overview

J-tau is a simulation framework for evaluating customer service agents. It measures accuracy in tool use and user interaction according to defined policies.

> [!IMPORTANT]
> This repository is a Japanese version based on [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench), and currently supports evaluation only for `telecom_ja`. For evaluating other English domains, please use the original repository.

## Supported Domains

### telecom_ja
A domain based on customer support for telecommunications services. The agent must access user information and instruct users to operate their own devices.

## Quickstart

### 1. Installation

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/sbintuitions/j-tau-bench.git
cd j-tau2-bench
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
  --num-trials 1 \
  --num-tasks 5
```

Results are saved to `data/simulations/` and can be viewed with `uv run tau2 view`.

## License
[Modified MIT License](LICENSE)

## Acknowledgements
We thank the tau-bench project for providing an excellent evaluation framework.
tau-bench is released under the [MIT License](https://github.com/sierra-research/tau-bench/blob/main/LICENSE).

## Citation

```
@misc{j-tau-telecom-2026,
  author       = {Chihiro, Yano and Jun, Hirako and Ryota, Hirobuchi},
  title    = {J-tau: A Japanese Benchmark for Tool-Agent-User Interaction in Real-World Domains},
  url = {https://github.com/sbintuitions/j-tau-bench},
  howpublished = {\url{https://github.com/sbintuitions/j-tau-bench}},
  year     = {2026},
  version  = {v202606}
}
```
