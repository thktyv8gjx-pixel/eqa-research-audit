> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# PTP 单条真实记录：字段与证据链审查

审查日期：2026-10-21。判定：**PARTIAL_ONLY**。本轮只有静态核查，没有模型推理、仿真或实验。实际取得图片数：**0**。

## 1. 固定来源与选择规则

- 论文：[Prune-Then-Plan，arXiv:2511.19768](https://arxiv.org/abs/2511.19768)。
- 官方仓库：`NoahFrahm/Prune-Then-Plan`；固定上一轮 commit：`b1e0304976bcfa33ffa5e367ede44e84a4a40676`。这是审查代码版本，**不是已经证实的轨迹生成版本**。
- [原始逐步 JSON](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/data/annotated_frontier_data.json)，git blob `41c9cc3a4ecf859f7f7dd37f033b1181076c6ec5`，官方树记录5,614,148字节；本地原件：`../sources/ptp/data/annotated_frontier_data.json`。
- 上轮 `../evidence/DEEPER_SCHEMA.json` 已记录 question ID `0f359392-b134-42f5-8715-5e3b68fa0973`、示例 step `1`。本轮固定此 question，不另选有利题目；在它的全部已标注 steps 中选择字段更完整的一条。
- 规则：比较 memory、frontier、三维 agent position、all-memory、classes及两组alignment的存在/长度一致性、PNG basename明确性，共8项；得分相同时取数字最小的step。**不读取答案、好坏标签或预期成败来排名**。step 1为4/8，step 2为8/8，所以选择 **step `2`**。完整只是字段形状完整，不是证据充分。程序与中间结果见 [audit_trace.py](../../SOURCE_INDEX.json)、[选择与原始记录](../../SOURCE_INDEX.json)。
- 联结：[348题校准QA](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/data/aeqa-questions-calibration.json)，按 `question_id` 精确匹配且仅一行。逻辑场景 `episode_history = 00817-X4qjx5vquwH`；问题与标准答案见官方JSON，本公开副本不再摘录逐题文本。这些是原始元数据，**没有该step实际回答或答错记录**，不能称它为已证实的baseline失败案例。

初始QA的 `position/rotation`，以及 `extra_property.position/rotation` 都确实存在。runner L132–150将前者作为起点，将extra位置用于目标距离相关逻辑；它们不是step 2的相机位姿或可合法获取证据的见证。`answer/extra_answers/extra_property/object_id/class` 保留为评估侧字段，不能作为部署策略的未来真值输入。

## 2. 所选记录字段（公开副本仅列schema与审计结论）

原始记录含15个键。为避免再分发逐行数据，完整向量、分数和原始摘录只保留本地。请按上述固定commit/question/step在官方JSON定位。

| 原始字段 | 本次审查事实 |
|---|---|
| `confidence_values` | 空；不推断模型失败 |
| `rgb_memory_snapshot_paths` | 3个引用，未取得像素 |
| `memory_snapshot_blip_alignment_scores` | 与memory引用等长，不是支持真值 |
| `rgb_frontier_snapshot_paths` | 2个引用，不是已执行动作 |
| `frontier_snapshot_blip_alignment_scores` | 与frontier引用等长，不是取证真值 |
| `prediction_set_size` / `prediction_set` | 不提供实际动作或不可恢复证明 |
| `all_memory_snapshots` / `all_memory_snapshot_blip_alignments` | 与memory列表/分数相同；不证明历史完整 |
| `agent_position` | 位置向量，无完整相机pose |
| `frontier_positions` / `frontier_positions_habitat_rotated` | 候选坐标及轴变换，无相机朝向/可达性保证 |
| `annotator_labels` | 有坏前沿标签，无实际执行结果 |
| `snapshot_img_classes` | 类别列表不是像素证据或楼层支持标注 |

## 3. 路径怎样解析，哪些资源实际存在

**代码已实现的读取约定。** [offline-calibration.yaml L1–4](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/cfg/offline-calibration.yaml#L1-L4) 定义根目录 `data/calibration_trajectories`。旧版已取得的 [calibration.py L159–174](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/src/calibration.py#L159-L174) 据question ID、`snapshot/`或`frontier/`拼接路径。因此需核验的5个精确文件是：

```text
data/calibration_trajectories/0f359392-b134-42f5-8715-5e3b68fa0973/snapshot/1-view_0.png
data/calibration_trajectories/0f359392-b134-42f5-8715-5e3b68fa0973/snapshot/2-view_2.png
data/calibration_trajectories/0f359392-b134-42f5-8715-5e3b68fa0973/snapshot/0-view_2.png
data/calibration_trajectories/0f359392-b134-42f5-8715-5e3b68fa0973/frontier/0_0.png
data/calibration_trajectories/0f359392-b134-42f5-8715-5e3b68fa0973/frontier/1_1.png
```

此外校准器会glob `snapshot/2-view_*.png`，按末尾view编号排序并读取最后一张作为egocentric输入。该模式只能导出待核路径规则，**不能证明实际有几张、哪张是最后一张、完整历史是否被包含**。

**实际取得。** 固定Git树98项、84个文件，唯一PNG为 `assets/teaser.png`；树内没有上述轨迹图片/逐图大小清单。原Git树已读，未下载teaser。README L88只提供一个Drive整包下载入口，L114给默认解压目录；没有所选5图的独立下载URL、大小、hash或run manifest。目录约定不等于包内已核文件索引。

**外部包尚未核实。** 官方下载入口文件ID为 `1uvXcEp_fpKjGnHKDPCa0eSTdOcGqKxNb`；[安全预览入口](https://drive.google.com/file/d/1uvXcEp_fpKjGnHKDPCa0eSTdOcGqKxNb/view)。web读取不可用，Chrome预览返回 `ERR_CONNECTION_TIMED_OUT`。未访问下载端点来获取payload，未下载整包或图片。包实际文件名、压缩格式、字节大小、内部清单、hash、具体图片大小：**UNVERIFIED**。README要求解压只能说明预期为归档包，不能确认ZIP格式。访问失败不是文件已删除或私人不可申请的证明。

**许可。** 仓库 [LICENSE](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/LICENSE) 为MIT，正文针对software及associated documentation。README另要求从[HM3D官方渠道](https://aihabitat.org/datasets/hm3d-semantics/)取得场景。未核实Drive图包的独立许可，不能把代码MIT或项目网页CC许可自动扩展到HM3D派生图片。所选图也没有已确认单图下载方式/大小，因此本轮没有下载一张来“试试看”。

## 4. 字段生成路径及状态对应的实质限制

以下均为固定commit静态源码事实，**未执行代码，也不声称该commit就是这条记录的生成器**。

1. [runner L208–284](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/evaluation/run_aeqa_evaluation.py#L208-L284)：先取多视角观察，命名 `{cnt_step}-view_{view_idx}.png`；`cam_pose`交给场景处理，但所读保存路径只保存RGB图，没有把该step全相机pose写入本条JSON。`scene_aeqa.py` L228–246确实在内存计算外参，不能据此称已发布外参。
2. [tsdf_planner.py L407–489](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/src/tsdf_planner.py#L407-L489)：部分frontier沿用旧图片；仅未有图时，从**当时智能体位置**转向frontier拍摄，命名 `{cnt_step}_{i}.png`。不是移动到frontier后的观察。选例step 2引用 `0_0.png`、`1_1.png`，不能把它们称为step 2同时采集的照片或反事实动作结果。`scene_aeqa.py` L248–277设置该位置/方向并取传感器输出，但没有发布逐图capture状态表。
3. [get_step_info L190–325](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/src/eval_utils_gpt_aeqa.py#L190-L325) 收集memory、类别及过滤后的路径；L1159–1172构造step_info；[query_vlm L119–127](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/src/query_vlm_aeqa.py#L119-L127) 添加agent及候选坐标。**发布记录有 `all_memory_snapshots`，但这个构造字典未输出该键；源码的all-memory alignment为映射，发布记录为列表；源码另有coverage/time字段而选例没有。** 未找到把此运行输出变为发布JSON的可核整理/标注流程与版本绑定。因此只能部分追溯，不能把列表名称当完整M_t/R_t契约。
4. `query_vlm` L276–286可记录 `selected_frontier_position`；对全部1632条发布记录静态计数，该键存在数为**0**。更关键的是[runner L435–497](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/evaluation/run_aeqa_evaluation.py#L435-L497)：dynamic commit条件下可以忽略新选择、继续旧目标，随后 `agent_step`才更新位置/朝向。因此候选、模型选择、控制器承诺目标、实际位移必须分别记录。
5. [logger L440–463](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/src/logger_aeqa.py#L440-L463) 以question/step替换字典；没有自动生成reset_state、反事实分支、像素hash或run身份。记录键相同不能排除重跑覆盖。该题只有step 1/2两个**标注条目**，缺step 3不等于轨迹在step 2结束。

## 5. 八项准入核对

| 核查项 | 状态及原始字段/文件 | 本轮判断 |
|---|---|---|
| 1 历史观察真实图片 | 路径 `DIRECTLY_AVAILABLE`；像素 `UNVERIFIED`。`rgb_memory_snapshot_paths`及calibration.py读取规则 | 0图取得；完整H_t及支持帧集合缺失 |
| 2 memory/frontier及同状态对应 | 引用列表 `DIRECTLY_AVAILABLE`；物理快照/可靠状态对应 `UNVERIFIED` | 只同属question/step；缓存图跨时刻，缺capture pose/time/hash及状态manifest，不可宣称同步 |
| 3 完整相机位置与朝向 | agent位置 `DIRECTLY_AVAILABLE`；逐图相机pose `UNAVAILABLE`（已读JSON） | 初始QA旋转、frontier轴变换、模板camera参数都不能补成逐图实测pose |
| 4 实际选取并执行动作 | `UNAVAILABLE`（已读JSON）；源码有选择及执行接口 | 无selected字段、旧承诺目标、真实action序列及成本，不能反推 |
| 5 该动作后的真实观察 | `UNAVAILABLE`（已读JSON）；外部归档 `UNVERIFIED` | 没有动作—后图关联；`2-view_2`在选动作前的当前观察链中，不是step 2动作后图 |
| 6 同初态其他合法动作结果 | `UNAVAILABLE`（已读发布资源）；要验证通常 `SIMULATOR_REQUIRED` | 无分支、reset state和合法性/结果记录；两个frontier不是两条已执行分支 |
| 7 合法行动及预算内取证 | `UNAVAILABLE`；模板 `num_step:50`仅 `CONFIG_ONLY` | 没有该run配置/剩余预算/行动成本/真实支持链，不能给R2见证，更不能给R4否定证书 |
| 8 存储/检索/视觉推理归因 | `UNAVAILABLE`；部分memory路径可读 | H_t像素、支持标注、完整M_t、实际模型输入R_t和实际回答缺失；两个列表相等不证明无遗漏，也不证明推理失败 |

这里的UNAVAILABLE限定为所审查发布文件，**不声称未读归档内部一定没有**；UNVERIFIED不能用于放行。即使随后取得5图，也不能自动填补第4–8项。

**论文原文与审计推断分开。** 原文§3.4称标注者只据当前问题、候选图和占据图判断坏前沿，不看未来帧/记忆；§4.1报告校准baseline使用Qwen2.5-VL 32B、50步上限。审计判断是：这些描述不构成本条记录的run/config身份，也不把bad标签变为取证失败真值。当前证据只能归入D1的“记录不足，无法判定”，不能赋成存储遗漏、检索遗漏、可恢复或不可恢复。

本轮9份新增官方文本均按Git blob验证；旧阶段一215份和阶段二138份原件hash不变。辅助检查见 [STATIC_CHECKS.json](../../SOURCE_INDEX.json)、[PRESERVATION_CHECK.json](../../SOURCE_INDEX.json)。
