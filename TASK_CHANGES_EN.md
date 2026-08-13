# Task Changes from tau2-bench

[日本語版](TASK_CHANGES.md)

This document records changes made to task content itself, separate from translation work.
There are two categories of changes:

1. **Fixes to preserve task quality after localization** — corrections for distortions introduced when adapting place names, personal names, language settings, etc. to the Japanese version
1. **Fixes to make unsolvable original tasks solvable** — corrections for tasks that were already unsolvable in the original due to missing arguments, contradictions, etc.

`telecom_ja` has no changes to task content itself (translation only), so it is not included in this document.

## Table of Contents

- [Fixes to preserve task quality after localization](#fixes-to-preserve-task-quality-after-localization)
  - [airline_ja](#airline_ja)
  - [retail_ja](#retail_ja)
- [Fixes to make unsolvable original tasks solvable](#fixes-to-make-unsolvable-original-tasks-solvable)
  - [airline_ja](#airline_ja-1)
  - [retail_ja](#retail_ja-1)

## Fixes to preserve task quality after localization

### airline_ja

| task id | change |
|---|---|
| 6, 7 | `user_scenario.known_info` only contained the romanized user ID, without the user's name in kanji. Appended the boilerplate sentence "あなたの名前は{姓} {名}です。" ("Your name is {last name} {first name}.") at the end. |
| 15 | `task_instructions` read "Since you live in Princeton, so EWR and PHL are equally convenient for you and you want to consider both." When replacing the airports with domestic Japanese ones (NRT/NGS), there was no suitable equivalent for the place of residence, so the reference to it was removed, leaving only "NRTとNGSはどちらも同じくらい便利であり、両方を検討したいと考えています。" ("NRT and NGS are equally convenient for you and you want to consider both."). Removing the residence information does not change the meaning of the task, so this is not a problem. |
| 24 | Trying to keep the "West Coast" destination condition after localization matched multiple airports, making it hard to narrow down to a single correct airport. Changed the setting to "Tohoku region," which corresponds to only one airport. |
| 39 | In a task where the user converses in a language that is not their native one, the original tau-bench set the user as a French native speaker. In J-tau, this was changed to a Chinese native speaker, since the characters that appear are closer to Japanese, matching the Japanese evaluation setting. |

### retail_ja

| task id | change |
|---|---|
| 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 35, 39, 45, 46, 47, 48, 56, 57, 58, 67, 68, 69 | `user_scenario.known_info` only contained the romanized user ID or email address, without the user's name in kanji. Appended the boilerplate sentence "あなたの名前は{姓} {名}です。" ("Your name is {last name} {first name}.") at the end. |

## Fixes to make unsolvable original tasks solvable

### airline_ja

| task id | change |
|---|---|
| 7 | `nl_assertions.3` ("Agent communicates that total cost of upcoming flights is $1,628.") was incorrect because it summed in the amount of an already-canceled flight. Corrected to the actual amount of $708 (¥106,200). |
| 29 | No payment method was specified, making it impossible to specify the correct action argument. Specified a payment method. |
| 32 | Neither a payment method nor a refund destination was specified, making it impossible to specify the correct action arguments. Specified both. What actually happens is a refund rather than a payment, but since it is a flight change, both were specified so that the user model would not deny a negative price difference. |
| 33 | No refund destination was specified, making it impossible to specify the correct action argument. Specified a refund destination. |
| 39 | No cancellation reason was specified, and the user model could potentially give a reason not covered by insurance. Restricted the cancellation reason to a health reason covered by insurance. |
| 44 | The task instructions state that flights of 3 hours or less including connection time should be upgraded to business class whenever possible, but the gold trajectory also upgraded a flight of 7.5 hours including connections. Fixed this. Also, no payment method was specified, making it impossible to specify the correct action argument, so a payment method was specified. |

### retail_ja

| task id | change |
|---|---|
| 18, 91, 107 | The task required the agent to "refuse an exchange for the same item," a behavior not documented in the policy. Fixed to allow the exchange. |
| 25 / 26 | The action required to complete id25 was placed under id26 instead. Removed the `transfer_to_human_agents` action from id26 and added it to id25. |
| 28 | The price of the garden hose was incorrect. Fixed it. |
| 38 | No cancellation reason was specified, making it impossible to specify the correct action argument. Specified a cancellation reason. |
| 64 | Added a condition so that the item to be exchanged can be narrowed down to one. |
| 99 | The payment card required by the evaluation criteria did not match the task description. Fixed it (credit_card_8105988 → credit_card_3951670). |
| 104 | The action's id number was incorrect. Fixed it. |
| 105, 110 | The evaluation criteria contradicted the DB state, requiring an exchange that could not actually be performed. Fixed it. |
