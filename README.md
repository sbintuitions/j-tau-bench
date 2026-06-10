# J-tau: A Japanese tau-bench for Benchmarking　Tool-Agent-User Interaction in Real-World Domains

J-tauは日本語環境に特化したエージェント能力の評価ベンチマークです。

## 概要

J-tauは、カスタマーサービスエージェントを評価するためのシミュレーションフレームワークです。ポリシーに従ったツール使用・ユーザー対話の正確さを測定します。


> [!IMPORTANT]
> 本リポジトリは [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench)を元に作成された日本語版で、現在`telecom_ja` のみを評価対象として利用可能です。その他のドメインを英語で評価する場合は、オリジナルリポジトリを利用してください。

## 対応ドメイン
### telecom_ja
通信事業のカスタマーサポートを題材としたドメインで、エージェントはユーザーの情報にアクセスしつつ、ユーザーに自身の端末を操作するよう指示を行う必要があります。

## クイックスタート

### 1. インストール

[uv](https://docs.astral.sh/uv/getting-started/installation/) が必要です。

```bash
git clone https://github.com/sbintuitions/j-tau-bench.git
cd j-tau2-bench
uv sync
```

### 2. APIキーの設定

[LiteLLM](https://docs.litellm.ai/docs/providers) 経由で各種プロバイダーに対応しています。

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
  --num-trials 1 \
  --num-tasks 5
```

結果は `data/simulations/` に保存されます。`uv run tau2 view` で閲覧できます。

<!-- ## `telecom_ja` ドメイン

`telecom` ドメインをベースに、日本語環境向けにローカライズしたドメインです。 -->

<!-- - **ポリシー・マニュアル・ワークフロー** — 全文を自然な日本語に翻訳
- **顧客データ** — 日本人名、日本の住所、日本の電話番号に変更
- **用語の統一** — 「セルラー通信」→「モバイル通信」など、日本の通信業界で一般的な表現に統一 -->

## ライセンス
[Modified MIT License](LICENSE)

## 謝辞
このベンチマークは[tau-bench](https://github.com/sierra-research/tau2-bench)をもとに作成しました。

tau-benchは[MITライセンス](https://github.com/sierra-research/tau-bench/blob/main/LICENSE)で公開されています。

## 引用

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