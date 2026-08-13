# tau2-bench 互換パッチ

[![English README](https://img.shields.io/badge/README-English-blue)](README_EN.md)

J-tau は `sierra-research/tau2-bench` をフォークして日本語ドメインを追加したものですが、
評価フレームワーク自体にも修正を加えています。

このディレクトリは、その差分を [`sierra-research/tau2-bench`](https://github.com/sierra-research/tau2-bench) の[特定コミット](https://github.com/sierra-research/tau2-bench/commit/f0927a4b9cdfa7b374269efaa29ff7fdac90d8fc)に対するパッチとして切り出し、公開するものです。
英語ドメインをオリジナル実装で評価する際に本ディレクトリのパッチを当てることで、J-tau側と同様のフレームワークで評価を行うことができます。
ただし、airline, retailドメインについては一部タスクの修正を行なっているため、J-tauとtau-benchの結果を直接比較することはできないことに注意してください。

## パッチの内容

| ファイル | 内容 |
|---|---|
| [`0001-orchestrator-error-classification.patch`](0001-orchestrator-error-classification.patch) | Orchestrator のエラーハンドリング修正 |
| [`0002-claude-prompt-cache.patch`](0002-claude-prompt-cache.patch) | Claude のプロンプトキャッシュ有効化 |

### 1. Orchestrator のエラーハンドリング修正（`0001-orchestrator-error-classification.patch`）

- **対象ファイル**: `src/tau2/orchestrator/orchestrator.py`

tau-benchでは`INFRASTRUCTURE_ERROR`として分類されリトライの後スコア集計から除外されていたエラーのうち、明らかにモデル自身の失敗であるものを正しく分類するパッチ。
具体的には以下の条件に該当する場合に発話者の失敗として分類し、スコアを0として集計する。

- content・tool_calls ともに空の出力で、`finish_reason` が `stop`もしくは`content_filter`であった場合
- tool call 引数の JSON 破損（`json.JSONDecodeError`）

### 2. Claude のプロンプトキャッシュ有効化（`0002-claude-prompt-cache.patch`）

- **対象ファイル**: `src/tau2/utils/llm_utils.py`

APIコストを下げるために、生成時に system メッセージと tools スキーマに `cache_control: {type: ephemeral}`引数
を付与し、Anthropic Claude の自動プロンプトキャッシュを有効化する。

## 適用方法

```sh
bash patches/apply.sh                       # -> ./tau2-bench-patched/
# または任意のディレクトリ名を指定
bash patches/apply.sh my-tau2               # -> ./my-tau2/
```
