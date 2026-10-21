> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# D1数据与实验准入审计

**当前阶段：阶段二准入审计完成；最终判定：HOLD。**

审查截止2026-10-21（Asia/Shanghai）。阶段一推荐不作为正确性前提。本轮只阅读、核查官方小文件并执行静态解析，未训练、推理、跑benchmark、启动Habitat/真机、租GPU或调用付费API。

## 先报告六项结果

1. **当前阶段**：D1“缺失证据的可恢复性”的数据/新颖性/实验准入审查；没有进入算法复现或研究实验。
2. **实际检查数量**：盘点并校验阶段一目录内**215份既有文件**，其中11份PDF作结构/页数检查；完整读取的核心材料为2张CSV、8篇笔记、4份阶段报告及1份阶段日志，共**15份**。另对**49份官方资源文件**做字段/源码/原文静态核验：14 JSON、2 CSV、19 Python、7 YAML、1提示词文本、1 shell、3 HTML、2 PDF。49包含数据树元数据，不等于49篇论文；215的hash检查不冒充全文精读。关键原文章节范围与来源见反证报告，参考文献和非D1附录未全部重读。
3. **关键反证**：[Active Perception for Embodied Disambiguation，2608.13605](https://arxiv.org/abs/2608.13605) p3已区分观察不足/意图歧义并实现观察—澄清—选择决策，p4–7报告匹配真机试验。该机制不能因换EQA名称而重新认定创新。PTP、Pred-EQA、HFLEX也已覆盖校准探索、定向补证据、近看物体/搜索未知房间等部分机制。
4. **数据可获得程度**：问答、逻辑场景ID、部分初始pose、EM帧索引和PTP局部前沿记录可读；**未获得任何一套能可靠支持全部五类的完整prefix—memory—action—observation—branch证据包**。未下载或检查原始视频/场景包，不把URL/文件名当像素，不把代码可生成当数据已发布。
5. **D1判定：HOLD**。宽泛机制已有强反证；剩余“同状态、动作/预算条件下的可恢复性认证与记忆链归因”仍有待核差异，但没有足量标签/实际失败模式或已核实执行环境支撑，不能放行方法实验。HOLD不表示新颖性已成立，也不以缺数据替D1保住方法贡献。
6. **下一步唯一优先任务**：核验PTP官方校准轨迹包中的**一个原始question/step**，检查能否取得对应真实帧、姿态、记忆/检索引用、实际前后动作与观察及可恢复状态/同状态替代结果。先清单/小子集，不能直接下载整个大包。若它仍只是图片+坏前沿标注，就停止把公开包当可恢复性真值；仿真/新数据采集另登记待授权。此任务只排除数据能否组成证据链的疑问，不承诺论文方向。

## A. 五种情形能否可靠区分

| 情形 | 本轮数据能支持什么 | 尚缺什么/当前结论 |
|---|---|---|
| 1 已看见但存储/检索失败 | 3D-Mem有作者失败图；PTP有部分快照引用列表 | 缺实际prefix像素、可靠支持集合及完整M_t/R_t记录；图例不能批量生成归因标签。正确证据已检索但仍认错另属感知/推理问题 |
| 2 尚未看见但允许探索能取得 | APED真机案例报告过正例；各主动方法会探索 | 公开QA/候选前沿不能证明某prefix存在预算内取证链；须实际见证动作链/合法重放，或可交互环境 |
| 3 意图/指代歧义需要澄清 | Abstain-A有RU/PD类别，APED有真实询问示例与对话 | 标签不随当前可见性/剩余动作更新；缺对应真实用户意图及多数样本的交互回应。暂时未观察全不等于本质意图歧义 |
| 4 给定动作/环境/预算不可取证 | 部分任务标为AL/IU；代码有预算和路径搜索 | AL/IU不是穷尽证书，失败/超时也不是。未找到完整状态/动作/可见性覆盖，不能可靠标注不可恢复 |
| 5 现记录无法判定 | 能明确列出缺字段和版本/权限缺口 | 应保留为5；不允许用模型猜标签或把所有缺证据都并入4 |

五类还可能在同一prefix并存，不能默认互斥或直接把Abstain五类改名。特别是不同记录的时间、状态和动作权限若不一致，拥有相同问题ID也不能证明是同一次观察过程。

## B. 决定性字段发现

### AbstainEQA

固定至commit `b970eb97aa6afce7020a0d57baaef79c53e05303`，[原始QA目录](https://github.com/gibrantaowu/AbstainEQA/tree/b970eb97aa6afce7020a0d57baaef79c53e05303/data/QA)。本地快照在 `EQA_STAGE2_GATE/sources/abstain/`。

- **主动版**两文件各184行，均有 `question_id/question/answer/episode_history/position/rotation`，都没有 `frame_list`。unanswerable另有 `category_un`；45 RU、34 FP、33 PD、29 AL、43 IU，是实际字段计数，不是模型实验指标。184对ID、scene、初始pose全部一致；这些pose由runner作为起点使用，不是支持证据位置。
- **记忆版**两文件各1636行，每行有整数 `frame_list`，但两个文件均没有 `category_un`；`category`是原QA能力类。1636对的episode和frame_list**完全一致**，而不是已核实的“原因帧集合”。列表能读取不代表其语义保证已经验证；无原图不能判它是否同时适合作支持/拒答依据。
- 已读EM baseline的 `sample_frame_paths` 对整段episode均匀取默认50帧，并未消费 `frame_list`。把全episode改成严格prefix需要独立审计wrapper；不得改原评测或假称原协议已验证prefix可恢复性。
- 帧提取代码能从外部 `agent_state`/ScanNet传感器记录生成像素与pose，但外部资产未取得。运行能力与实际文件可读性分开。

出处：[schema全量计数](../SOURCE_INDEX.json)、[配对核查](../SOURCE_INDEX.json)、[索引深查](../SOURCE_INDEX.json)。

### Prune-Then-Plan

固定至commit `b1e0304976bcfa33ffa5e367ede44e84a4a40676`，[校准记录](https://github.com/NoahFrahm/Prune-Then-Plan/blob/b1e0304976bcfa33ffa5e367ede44e84a4a40676/data/annotated_frontier_data.json)。

- 203问题、1632个step；有 `agent_position/frontier_positions/frontier_positions_habitat_rotated`、`rgb_memory_snapshot_paths/rgb_frontier_snapshot_paths/all_memory_snapshots`、`annotator_labels` 等。不是完整相机位姿、实际动作和结果；没有策略完整checkpoint。
- `confidence_values`全1632步为空；`good_choices`全空；每step有非空 `bad_choices`。坏前沿人工标签评价当前相关性/几何，不是“执行该动作仍无法取证”的结果。原文§3.4明确标注者不看future frames/memory。
- 记录共引用6038个memory图片路径和6403个frontier图片路径，**计的是引用而非唯一图片数**；对应图包未取得。完整路径图像、动作、预算与状态不能从这些字符串自动重建。
- 203/203可联结348条校准QA；与3D-Mem/Abstain-A的184题没有共同ID。无法直接把拒答原因和局部前沿步骤拼在一起。
- 573行文件只有557个唯一ID，16个ID重复，且包含全部348个校准ID和203个已标注ID。这**不证明原作者泄漏**，但复用时必须核真实测试manifest；不能把573行全量文件直接作独立测试，也不在本轮擅自去重/重划分。

出处：[PTP连接与去重审计](../SOURCE_INDEX.json)。

### GraphEQA、Pred-EQA、HFLEX与3D-Mem

- GraphEQA `open-eqa-choices.json`有295个字典键，`openeqa_init_trajs.json`有63个episode。`full_traj_pos`只是位置列表，不能补成逐帧旋转、时间、动作或反事实分支。
- 3D-Mem/Pred的184题文件是真实可读QA/初始条件，不含支持帧、实际prefix或拒答原因。logger存在不等于已获得完整发布日志；3D-Mem的 `success_list` 也不能直接当“有充分支持证据”的真值。
- Graph和HFLEX已有接近已见物体、探索前沿/未知房间与信心停止。Graph所读OpenEQA runner为20规划循环；HFLEX所读ROS配置的 `max_episodes:50` 是总episode数，**不能当每题探索预算**。HFLEX论文另报告迭代预算，但实现控制器上限本轮尚未全部核对。
- HFLEX floorplan、语义网格等额外先验须单独声明；完整轨迹的位置序列、评价答案、原因标签及未执行分支结果均不得流入部署策略。

各项原始键、来源、文件与限制均在[DATA_FIELD_MATRIX.csv](DATA_FIELD_MATRIX.csv)。

## C. 矩阵状态如何理解

矩阵为10个数据/协议单元×17项，共170行：44项DIRECTLY_AVAILABLE、10项DERIVABLE、23项SIMULATOR_REQUIRED、75项UNAVAILABLE、18项UNVERIFIED。它是字段级盘点，包含共享基准与不同版本/任务单元，**不是170个独立样本，也不是数据可用率或研究成功率**。

- DIRECTLY_AVAILABLE仅表示该行具体字段/代码接口或论文表格确实可读；partial字段的限制必须一起读，不能把索引升级成像素/语义真值。
- DERIVABLE逐行给精确联结/原行身份的做法与假设；不模糊匹配、不生成新划分。
- SIMULATOR_REQUIRED表示验证未执行动作后果/环境可达必须取得交互状态；有模拟器也不自动获得不可恢复证明。
- UNAVAILABLE表示在本轮审查的文件中未找到可用记录，不断言全球/所有版本没有；UNVERIFIED表示有发布声明、外部资产或部分字段但未完成内容核验。

## D. 为何是HOLD

不能判为GO：直接近邻已覆盖宽泛主张；五类标签缺口、同状态分支/完整记忆链、实际测试manifest与4060执行条件都没有齐备证据。

也不凭单篇论文断言全部严格问题已被解决：APED的目标消歧正例没有覆盖所有存储/检索失效和动作/预算条件下负例证书；本轮也未找到能否定这一更严格审计问题的完整实现。因此当前只保留一个待证实的严格差异，**冻结方法实验和“创新成立”表述**。若最小证据链核查失败、或简单方法/直接近邻已经解决同一严格问题，再终止D1候选，不把“更难收数据”当研究贡献。

**RTX4060 8GB：没有已核实的端到端EQA执行方案。** 本轮轻量解析可在CPU完成；原代码的远端VLM配置、HFLEX注释中的量化endpoint、作者使用的更大机器都不能证明本地能跑。云、付费API、场景/权重、Habitat及真机均未动用。

## E. 交付与留痕

1. [字段矩阵](DATA_FIELD_MATRIX.csv)
2. [新颖性反证](NOVELTY_COUNTEREVIDENCE.md)
3. [有条件最小实验协议](MINIMAL_EXPERIMENT_PLAN.md)
4. [本审计报告](STAGE2_GATE_REPORT.md)

辅助证据在 `EQA_STAGE2_GATE/evidence/`；新增原文/源码/标注在 `EQA_STAGE2_GATE/sources/`；[本轮日志](logs/WORK_LOG.md)记录读取、网络失败与补救。GitHub网络DNS读取失败后使用已授权的GitHub连接器；大于1MB的contents空响应没有被判作空数据，改以已知blob SHA读取并核验完整JSON。没有绕过许可、下载大包或执行源码。

[验收记录](../SOURCE_INDEX.json)逐项记录矩阵、文件和原件hash检查。阶段一215份原件的本轮前后SHA256一致。阶段二准入审计到此停止；不自动进入最小实验。
