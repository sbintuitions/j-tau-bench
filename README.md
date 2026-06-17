# J-tau: A Japanese tau-bench for Benchmarking　Tool-Agent-User Interaction in Real-World Domains

[![English README](https://img.shields.io/badge/README-English-blue)](README_EN.md)

## 概要

J-tauは日本語エージェント能力を評価するベンチマークです。
カスタマーサービスシナリオの中で、ポリシーに従ってツール使用・ユーザー対話を正確に行う能力を測定します。


本リポジトリは [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench)を元に作成された日本語版で、現在`telecom_ja` のみを評価対象として利用可能です。その他のドメインを英語で評価する場合は、オリジナルリポジトリを利用してください。

## 対応ドメイン
### telecom_ja
通信事業のカスタマーサポートを題材としたドメインで、エージェントはユーザーの情報にアクセスしつつ、ユーザーに自身の端末を操作するよう指示を行う必要があります。

## クイックスタート

### 1. インストール

[uv](https://docs.astral.sh/uv/getting-started/installation/) が必要です。

```bash
git clone https://github.com/sbintuitions/j-tau-bench.git
cd j-tau-bench
uv sync
```

### 2. APIキーの設定

```bash
cp .env.example .env
# .env に API キーを記入
```

### 3. 評価の実行


```bash
uv run tau2 run \
  --domain telecom_ja \
  --agent-llm <llm_name> \
  --user-llm <llm_name> \
  --num-trials 1
```
| 引数 | 説明 |
|------|------|
| `--agent-llm` | エージェントに使用するLLM（[LiteLLM形式](https://docs.litellm.ai/docs/providers)で指定） |
| `--agent-llm-args` | エージェントLLMに渡す追加引数（JSON形式）。`api_base` 等も指定可 |
| `--user-llm` | ユーザーシミュレーターに使用するLLM |
| `--user-llm-args` | ユーザーシミュレーターLLMに渡す追加引数（JSON形式） |
| `--num-trials` | 各タスクの試行回数 |
| `--num-tasks` | 実行するタスク数 |

vLLM でサーブしたモデルを利用する場合は、LiteLLM形式に従い、以下のようにモデル名と`api_base`を指定します。

```bash
uv run tau2 run \
  --domain telecom_ja \
  --agent-llm hosted_vllm/<agent_model_name> \
  --agent-llm-args '{"api_base": <agent_api_base>}' \
  --user-llm hosted_vllm/<user_model_name> \
  --user-llm-args '{"api_base": <user_api_base>}' \
  --num-trials 1
```


結果は `data/simulations/` に保存されます。`uv run tau2 view` で閲覧できます。


## ライセンス
[Modified MIT License](LICENSE)

## 謝辞
優れた評価フレームワークを提供してくださった [tau-bench](https://github.com/sierra-research/tau2-bench) プロジェクトに感謝します。
tau-bench は [MIT ライセンス](https://github.com/sierra-research/tau-bench/blob/main/LICENSE) のもとで公開されています。

## 引用

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
