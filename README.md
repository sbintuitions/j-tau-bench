# J-tau: A Japanese tau-bench for Benchmarking　Tool-Agent-User Interaction in Real-World Domains

[![English README](https://img.shields.io/badge/README-English-blue)](README_EN.md)
[![テックブログ](https://img.shields.io/badge/Blog-telecom_ja-orange)](https://www.sbintuitions.co.jp/blog/entry/2026/06/19/100154)

## 概要

J-tauは日本語エージェント能力を評価するベンチマークです。
カスタマーサービスシナリオの中で、ポリシーに従ってツール使用・ユーザー対話を正確に行う能力を測定します。

本リポジトリは [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench)を元に作成された日本語版で、現在`telecom_ja`、`airline_ja`、`retail_ja` のみを評価対象として利用可能です。その他のドメインを英語で評価する場合は、オリジナルリポジトリを利用してください。

## 対応ドメイン

### telecom_ja

通信事業のカスタマーサポートを題材としたドメインで、エージェントはユーザーの情報にアクセスしつつ、ユーザーに自身の端末を操作するよう指示を行う必要があります。

### airline_ja

航空事業のカスタマーサポートを題材としたドメインで、エージェントはユーザーの予約情報にアクセスしつつ、フライトの変更・キャンセル・払い戻しなどをポリシーに従って処理する必要があります。

### retail_ja

小売業のカスタマーサポートを題材としたドメインで、エージェントは本人確認を行った上で、注文のキャンセル・変更、返品・交換、住所変更などをポリシーに従って処理する必要があります。

`retail_ja`と`airline_ja`では、翻訳作業に加えてタスク内容自体にも変更を加えています。詳細は[TASK_CHANGES.md](TASK_CHANGES.md)を参照してください。

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

### NL Assertions評価について（retail_jaドメイン）

`retail_ja`ドメインの一部タスクは、報酬の一部をLLMによる対話内容の評価で判定します。他のドメインではこの評価は使われません。

デフォルトでは `http://localhost:8000/v1` で稼働するvLLMサーバー上の `gpt-oss-120b` モデルを使う設定になっています。
LiteLLM形式に従い、以下のようにモデル名と`api_base`を指定することができます。

```bash
export TAU2_NL_ASSERTIONS_MODEL=hosted_vllm/<nl_assertion_model_name> TAU2_NL_ASSERTIONS_API_BASE=http://<host>:<port>/v1
```

以下のようにAPIモデル名を指定する場合には、`TAU2_NL_ASSERTIONS_API_BASE`は不要です。

```bash
export TAU2_NL_ASSERTIONS_MODEL=gpt-5-mini-2025-08-07
```

| 環境変数 | 説明 |
|------|------|
| `TAU2_NL_ASSERTIONS_MODEL` | nl_assertion評価に使用するモデル名|
| `TAU2_NL_ASSERTIONS_API_BASE` | ローカルでホストしたモデルを使う場合のサーバーURL |

## オリジナル実装（tau2-bench）との比較

J-tau は日本語ドメインの追加に加えて、評価フレームワーク自体にもエラー分類の見直し、Claude 向けプロンプトキャッシュの有効化といった修正を加えています。

英語ドメインにも同様の修正を加えて評価を行いたい場合には、
[patches/](patches/) 以下のパッチをオリジナルリポジトリに適用してから実行してください。修正内容の詳細は
[patches/README.md](patches/README.md) を参照してください。
ただし、airline, retailドメインについては一部タスクの修正を行なっているため、J-tauとtau-benchの結果を直接比較することはできないことに注意してください（詳細は[TASK_CHANGES.md](TASK_CHANGES.md)を参照）。

```bash
bash patches/apply.sh   # -> ./tau2-bench-patched/ にパッチ適用済みのリポジトリを生成
```

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
