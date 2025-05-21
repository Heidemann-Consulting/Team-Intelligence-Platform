# ApexFusion Workflow Library

**Version:** 1.0
**Date:** May 17, 2025
**Author:** Heidemann Consulting
**License:** Apache 2.0

Administrator imports YAML definitions into TIP » Process Workflows.

| Workflow Name | Input Document(s) | Output Document | Steps (high-level) | Runs | Human Review? |
|---------------|-------------------|-----------------|--------------------|------|---------------|
| **ApexFusion_DailyLogWorkflow** | Meeting notes OR free text | `Daily_Log_<date>` | Pre-summarise → Apply Daily_Log prompt → Generate doc | Manual trigger after stand-up | ✓ |
| **ApexFusion_DailyPlanWorkflow** | `Daily_Log_<date>` ▫ `Weekly_Sprint_<week>` ▫ `Task_Backlog` | `Daily_Plan_<date>` | Synthesise context → LLM plan draft → Self-critique | Manual (post-log) | ✓ |
| **ApexFusion_WeeklyReviewWorkflow** | All `Daily_Log_*` of week ▫ `Weekly_Sprint_<week>` | `Weekly_Review_<week>` | Concatenate → LLM summary → Metrics snapshot | Friday 16:00 (Time-based) | ✓ |
| **ApexFusion_SprintKickoffWorkflow** | `Weekly_Review_<prev>` ▫ KPIs ▫ `Backlog` | `Weekly_Sprint_<week>` | Analyse deltas → Suggest focus & capacity | Monday 09:00 (Time-based) | ✓ |
| **ApexFusion_MonthlyStrategyCheckWorkflow** | Last 4 `Weekly_Review_*` ▫ `North_Star_Charter` | `Monthly_Strategy_Check_<YYYY-MM>` | Trend clustering → Gap analysis → Recommendations | 1st business day | ✓ |
| **ApexFusion_ContextShrinkerWorkflow** | Any large doc > 6 K tokens | `Shrunk_<orig>` | Token count → Iterative 3-step compression | On demand | Optional |
| **ApexFusion_PromptWorkshopWorkflow** | `Prompt_Workshop_<date>` | Updates target workflow prompt field | Parse new draft → Run test suite → Store version | At workshop end | ✓ |
| **ApexFusion_DecisionLogWorkflow** | Any doc tagged `#decision` | `Decision_Record_<id>` | Extract decision block → Create ADR | Continuous | Optional |

**Document-name alignment:** every output listed above is later referenced exactly as an input elsewhere—no prefixes—ensuring seamless chaining.
