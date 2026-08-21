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
| [`0003-exclude-user-error-from-metrics.patch`](0003-exclude-user-error-from-metrics.patch) | `USER_ERROR` をスコア集計から除外し再実行対象にする |
| [`0004-nl-assertions-config.patch`](0004-nl-assertions-config.patch) | NL Assertions評価のモデル/api_baseを環境変数で設定可能にする |
| [`0005-user-review-critical-severity.patch`](0005-user-review-critical-severity.patch) | userモードのreview judgeでcriticalなユーザーエラーが破棄される問題を修正 |

### 1. Orchestrator のエラーハンドリング修正（`0001-orchestrator-error-classification.patch`）

- **対象ファイル**: `src/tau2/orchestrator/orchestrator.py`

tau-benchでは`INFRASTRUCTURE_ERROR`として分類されリトライの後スコア集計から除外されていたエラーのうち、明らかにモデル自身の失敗であるものを正しく分類するパッチ。
具体的には以下の条件に該当する場合に発話者の失敗として分類し、スコアを0として集計する。

- content・tool_calls ともに空の出力で、`finish_reason` が `stop`・`content_filter`・`length` のいずれかであった場合
- tool call 引数の JSON 破損（`json.JSONDecodeError`）

逆に `finish_reason` が取得できない場合（`None`）や未知の値であった場合は、発話者の責任と判断する材料がないため、
リトライののち `INFRASTRUCTURE_ERROR` として扱う。判定できないものを発話者の失敗として採点すると、
serving 側の異常がそのままスコアに混入してしまうため。

また `AGENT_ERROR` / `USER_ERROR` で終了した場合、その原因（例外メッセージと `finish_reason`）を
`SimulationRun.info` に記録する。違反したメッセージは trajectory に含まれないため、
これがないと後から原因を特定できない。

### 2. Claude のプロンプトキャッシュ有効化（`0002-claude-prompt-cache.patch`）

- **対象ファイル**: `src/tau2/utils/llm_utils.py`

APIコストを下げるために、生成時に system メッセージと tools スキーマに `cache_control: {type: ephemeral}`引数
を付与し、Anthropic Claude の自動プロンプトキャッシュを有効化する。

### 3. `USER_ERROR` をスコア集計から除外（`0003-exclude-user-error-from-metrics.patch`）

- **対象ファイル**: `src/tau2/data_model/simulation.py`, `src/tau2/metrics/agent_metrics.py`, `src/tau2/runner/checkpoint.py`, `src/tau2/utils/display.py`, `src/tau2/scripts/view_simulations.py`

`USER_ERROR` は user simulator 側の出力不良で打ち切られたものであり、agent の性能に帰属できない。
そのため `INFRASTRUCTURE_ERROR` と同様の扱いに変更する。

- `EXCLUDED_TERMINATION_REASONS`（`INFRASTRUCTURE_ERROR` と `USER_ERROR`）を定義し、スコア集計の分母から除外する
- チェックポイントから再開する際は再実行対象にする（除外したまま残すと trial 数が不足し `pass^k` が計算できなくなるため）
- ビューアおよびサマリ表示で、採点対象の失敗（`AGENT_ERROR`）と除外される失敗（`USER_ERROR` / `INFRASTRUCTURE_ERROR`）を別の色・記号で区別する

### 4. NL Assertions評価のモデル/api_base設定（`0004-nl-assertions-config.patch`）

- **対象ファイル**: `src/tau2/config.py`

upstreamの`retail`ドメインにも`nl_assertions`（LLMによる対話内容評価）を使うタスクが含まれているが、
デフォルトのモデル指定がコード内に固定されていた。J-tauと同様に環境変数で上書きできるようにする。

デフォルトは J-tau 側と同様 `hosted_vllm/gpt-oss-120b`（`http://localhost:8000/v1`で稼働するローカルvLLMサーバー）に変更される点に注意。
upstream本来のデフォルトだった `gpt-4.1-2025-04-14`（ホスト型API、ローカルサーバー不要）を使いたい場合は、以下のように環境変数を設定すること。

```bash
export TAU2_NL_ASSERTIONS_MODEL=gpt-4.1-2025-04-14
```

| 環境変数 | 説明 |
|------|------|
| `TAU2_NL_ASSERTIONS_MODEL` | nl_assertion評価に使用するモデル名 |
| `TAU2_NL_ASSERTIONS_API_BASE` | ローカルでホストしたモデルを使う場合のサーバーURL |

### 5. userモードのreview judgeでcriticalなユーザーエラーが破棄される問題を修正（`0005-user-review-critical-severity.patch`）

- **対象ファイル**: `src/tau2/data_model/simulation.py`

`review_llm_judge_user_only.py`のLLM judgeは`severity`として`"minor"` / `"critical_helped"` / `"critical_hindered"`のいずれかを返すが、
これを格納する`UserOnlyReviewError.severity`のPydanticスキーマは`Literal["minor", "critical"]`のままだった。
そのため judge が `critical_helped` / `critical_hindered` を返すたびに `UserOnlyReviewError` の構築時にバリデーションエラーとなり、
そのcriticalなユーザーエラーが結果から失われていた。スキーマを`Literal["minor", "critical_helped", "critical_hindered"]`に合わせて修正する。

## 適用方法

```sh
bash patches/apply.sh                       # -> ./tau2-bench-patched/
# または任意のディレクトリ名を指定
bash patches/apply.sh my-tau2               # -> ./my-tau2/
```
