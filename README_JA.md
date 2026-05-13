# J-tau: 日本語ドメインにおけるツール・エージェント・ユーザーインタラクションのベンチマーク

本リポジトリは [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench) の日本語版フォークです。

## 概要
$\tau$-bench は、カスタマーサービスエージェントをシミュレーション環境で評価するためのフレームワークです。ポリシーに従ったツール使用・ユーザー対話の正確さを測定します。

> [!IMPORTANT]
> 本リポジトリでは現在、`telecom`ドメインの日本語版、 `telecom_ja` のみを評価対象として利用可能です。

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
# 日本語ドメイン（telecom_ja）で実行
tau2 run \
  --domain telecom_ja \
  --agent-llm <llm_name> \
  --user-llm <llm_name> \
  --num-trials 1 \
  --num-tasks 5
```

結果は `data/simulations/` に保存されます。`tau2 view` で閲覧できます。

<!-- ## `telecom_ja` ドメイン

`telecom` ドメインをベースに、日本語環境向けにローカライズしたドメインです。 -->

<!-- - **ポリシー・マニュアル・ワークフロー** — 全文を自然な日本語に翻訳
- **顧客データ** — 日本人名、日本の住所、日本の電話番号に変更
- **用語の統一** — 「セルラー通信」→「モバイル通信」など、日本の通信業界で一般的な表現に統一 -->

## ライセンス

[Modified-MIT License](LICENSE)
