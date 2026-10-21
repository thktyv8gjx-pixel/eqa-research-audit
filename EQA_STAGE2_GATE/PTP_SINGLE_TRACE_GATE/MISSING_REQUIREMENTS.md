> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# D1仍缺失什么：资源条件与替代来源

当前仅支持 **PARTIAL_ONLY**。主来源：[PTP固定commit](https://github.com/NoahFrahm/Prune-Then-Plan/tree/b1e0304976bcfa33ffa5e367ede44e84a4a40676)，[论文2511.19768](https://arxiv.org/abs/2511.19768)。对应真实记录及8项核查见 [TRACE_EVIDENCE.md](TRACE_EVIDENCE.md)。不把未知包内容写成确定缺失。

| D1必需材料 | 当前缺口 | 取得条件/可接受替代 | 单独取得后仍不能解决什么 |
|---|---|---|---|
| 真实观察前缀H_t | 只有部分memory/frontier引用，无像素和完整历史manifest | 官方授权小子集；每图路径、字节大小、hash、capture time/state、许可。Drive归档内容未核，不请求整包下载 | 一张图不能证明前缀完整或“以前没看到” |
| 逐图相机外参、内参与场景版本 | 只有agent position、起点pose和模板相机设置 | 实际run传感器pose/capture表、scene asset版本/hash；不能用模板回填冒充实测 | pose本身不证明证据可辨/路线合法 |
| 记忆与模型实际输入 | 两组memory路径相同；发布schema与当前构造代码不完全一致 | 实际H_t→M_t→过滤/检索R_t→发送给回答器的逐项hash，以及相应producer commit/config | all-memory命名与类别列表不是完整支持语义或检索正确性证明 |
| 动作执行与后观察 | 未保存于已读JSON；候选/选择与实际执行有差别 | controller committed target、executed action、post-state/observation及成本的同run关联；官方小run日志可作正事实链 | 单条实际路线仍无其他行动的结果 |
| 同一初态的合法替代分支 | 无可用reset/branch/outcome证据 | 已记录且可核同状态分支；或另行授权交互仿真，固定场景/传感器/地图/记忆/控制器承诺/随机状态 | 只恢复位置不足以恢复同状态；不能用未来真值指导部署策略 |
| 剩余预算及取证证书 | 模板50个规划循环，不是原始行动/帧/时间预算；所选run配置未知 | 明确动作集合、成本函数、prefix已花费及剩余量；可恢复须一条成本≤B的真实支持链 | 一次失败/坏frontier/导航连通性不能证明不可恢复；负例须有限状态覆盖或范围明确的约束证书 |
| 正确支持和实际失败 | 本条有QA及plant类别，没有支持标注、实际回答或拒答原因 | 独立核验的支持集与回答/决策记录，评估信息隔离 | gold答案或 `extra_property`位置不是部署时可访问证据 |
| 策略身份与版本对应 | 审查commit已固定，原生成commit/checkpoint/config/run_id未绑定 | 作者发布的run manifest或足够可核的生成元数据 | README模型列表不证明本样本由某模型生成，更不证明4060能运行 |

## 单图资源请求登记：当前不执行

若以后为了核对路径语义需要一张图，可先指定选例已引用的 `snapshot/2-view_2.png`，理由是它是选中step的明确memory引用，不根据图像内容选取。所需来源为README所链接归档内该question目录；必须先取得**精确文件索引、实际字节大小、独立或受限解包下载方式、许可与hash**。这些当前均未核实，故不下载。

该图即使真实存在，也最多检查像素和路径是否吻合；不能代替动作分支、历史完整性、预算及支持标注。因此不把“下载5图看看”列为下一项研究优先任务。

## 潜在替代来源：仅为条件选项，未构成新准入

- [OpenEQA官方资源](https://github.com/facebookresearch/open-eqa)、[3D-Mem](https://github.com/UMass-Embodied-AGI/3D-Mem)及[Habitat/HM3D](https://aihabitat.org/datasets/hm3d-semantics/)可提供任务/交互环境的基础。需分别取得许可、核本机兼容性及完整状态重置/记录能力；本轮没有启动环境、下载场景或确认RTX4060 8GB端到端可运行。它们是申请交互资源的候选入口，不是已获得反事实数据。
- [AbstainEQA，2512.04597](https://arxiv.org/abs/2512.04597)提供任务级拒答与部分帧索引；上轮已核其字段，不能拼到PTP不同历史上冒充同状态取证标签。它可能服务离线拒答/证据诊断，不能补齐本次D1分支链。
- [Active Perception for Embodied Disambiguation，2608.13605](https://arxiv.org/abs/2608.13605)已构成宽泛观察/澄清决策的新颖性反证；上一轮没有取得官方完整逐步包，本轮不把它当现成替代数据。

## 唯一下一步建议

**停止依赖PTP公开记录推进D1最小实验，提交一次“可重置、可记账的交互仿真资源”申请。** 申请应先说明场景许可、小范围状态重置、动作成本、支持核验与记录契约，费用/下载/运行权限另批。若资源申请不获批准，再由导师另选候选；本轮不自行切换到开发或实验。

这条建议直接解决“是否能产生同初态合法分支及预算内取证见证”的关键缺口。若没有这类材料，仅补照片或增加模型不能把本次PARTIAL_ONLY升级为READY。
