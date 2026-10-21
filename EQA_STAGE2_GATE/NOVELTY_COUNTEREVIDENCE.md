> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# D1新颖性反证审查

审查日：2026-10-21。候选为“缺失证据的可恢复性”，本文件不预设阶段一推荐正确。结论标签见最终报告；没有运行任何研究实验。

## 最强反证：阶段一遗漏了直接先行工作

[Active Perception for Embodied Disambiguation，arXiv:2608.13605v1](https://arxiv.org/abs/2608.13605v1)，本地[原文](../SOURCE_INDEX.json)，p3 §III–IV明确区分：

- **Observation incompleteness**：所需物理证据没在当前观察中，可以改变视角/搜索取得；包括目标已见但细节未见，以及目标未进入当前候选集合。
- **Semantic or intent ambiguity**：环境足够可见，但用户偏好/意图未知；观察不能代替澄清。
- 决策 α∈{O,Q,S}：获取新观察、询问用户、选择目标；可重复观察，可在询问后再观察。

这属于**作者已实现并报告真机验证**，不是未来工作。p4 §V报告9个匹配场景、每场景4方法，共36次试验；p6表I列明证据来源、观察数、询问数，p7表II给对话。A8/A9包含搜索初始视野外目标。已核对[表I渲染](../SOURCE_INDEX.json)。未找到可读的官方逐步数据/代码发布，故实现细节属于论文报告，不能冒称已源码复核。

**审计判断：** “观察不足vs意图歧义”“继续看/问/选择”已被直接覆盖。把目标选择换成EQA回答、把桌面换成房间，均不能单独构成D1创新。9场景规模、无公开代码等局限不抹去已存在的贡献。它没有据本轮证据建立“在完整动作集合与剩余预算下穷尽证明不可恢复”，也没有发布可辨认存储/检索失效的完整中间状态；因此不把它夸大成覆盖全部五类审计任务。

## 逐项最近邻对照

| 来源 | 论文已经实现/报告 | 静态代码或发布文件确证 | 明确未来工作与尚未证明之处 |
|---|---|---|---|
| [AbstainEQA，2512.04597](https://arxiv.org/abs/2512.04597)，[正式正文](https://openaccess.thecvf.com/content/CVPR2026/papers/Wu_When_Robots_Should_Say_I_Dont_Know_Benchmarking_Abstention_in_CVPR_2026_paper.pdf) p3–8；[补充](https://openaccess.thecvf.com/content/CVPR2026/supplemental/Wu_When_Robots_Should_CVPR_2026_supplemental.pdf) p9 E.1–E.2 | 任务级五类拒答原因、回答/拒答评测、3D-Mem主动探索行为分析 | A版184条不可答题有category_un；EM两文件没有该字段。A版无frame_list；EM索引成对完全相同。EM基线按整个episode均匀采样，不读取frame_list | 支持帧对齐、继续探索/停止/问用户在E.2为未来方向；**不能说这些策略已由该文实现**。任务级IU/AL标签不等于动作/预算条件下不可恢复证书 |
| [3D-Mem，2411.17735v5](https://arxiv.org/abs/2411.17735v5)，[原文](https://arxiv.org/pdf/2411.17735) p3–5、10–14 | 快照记忆+前沿探索；已披露选错快照、漏检未入记忆、正确快照仍认错和问题歧义 | query_vlm_aeqa.py返回snapshot/frontier；runner把position/rotation用作初始pose；logger保存统计和可视化的能力存在，但未取得发布的完整run包 | 失效图不提供可批量重放的全部prefix、memory checkpoint和替代动作结果。选到正确帧仍答错属于感知/推理失效，不能强塞为“存储/检索失败” |
| [GraphEQA，2412.14480](https://arxiv.org/abs/2412.14480)，[原文](https://saumyasaxena.github.io/grapheqa/grapheqa_2025.pdf) p3–6、9、19–20 | 近看物体/探索前沿、回答信心与停止；承认过度自信/歧义 | GPT planner定义Goto_object_node_step/Goto_frontier_node_step；OpenEQA runner为20轮，并以is_confident或confidence_level>0.9停止。_answer在所读代码用于输出记录，构造messages未见注入gold | “预计接近物体会有用”不是取证可达性的标签或保证；未见澄清动作。只审过指定GPT路径，不替其他backend作无泄漏保证 |
| [Prune-Then-Plan，2511.19768](https://arxiv.org/abs/2511.19768)，[全文HTML转文](../SOURCE_INDEX.json) §3.1–3.6 | 校准坏前沿、剪枝、最近前沿规划；原文说明α是行为超参数，不是此设置下严格的族错误率保证 | annotated_frontier_data.json有203问题/1632步；203/203可联结348校准问答。bad_choices逐步存在，good_choices及confidence_values全空；图像文件仅有路径引用 | 标注者只看当前几何/前沿，不看future frames/memory（§3.4）。**坏前沿≠该题不可恢复**，空confidence_values不是校准已可直接复算，未执行分支没有真实结果 |
| [Pred-EQA，CVPR 2026原文](../SOURCE_INDEX.json)，[官方实现](https://github.com/yuanrr/Pred-EQA) | p4–5 §3.3–3.5：预测缺哪类证据及可能位置，执行后验证/修正假设；分离结构记忆与问题相关视觉证据 | src/pred_eqa.py、logger及184题文件可读；不是仅有README | 已覆盖“找到缺口→定向取证→修正规划/记忆”的宽泛机制。没有从已读材料确认严格的可恢复/不可恢复标签、澄清通道或所有分支证明 |
| [HFLEX-EQA，2609.26360](https://arxiv.org/abs/2609.26360)，[全文](../SOURCE_INDEX.json) §III–V | 近看已见物体、已知房间探索、搜索未见房间；按答案信心继续或停止；使用可选平面图先验 | OutputMode枚举explore_room/find_room/go_to_objects，另有answered/confidence；提示词明确低置信通常继续探索；没有ask/clarify枚举 | 地图先验改变信息权限。论文的无选项真机结果使用记录回放，不能据此声称另一策略闭环路线已验证。未见穷尽不可恢复证明 |

代码快照均在 `EQA_STAGE2_GATE/sources/`；各文件相邻fetch元数据给上游commit/blob。PTP、HFLEX锁至阶段一公开页面可核commit；hflex_ros/main与其他默认分支文件只锁本轮blob/hash，不冒称整个依赖栈版本齐全。

**数据划分额外核查。** PTP校准QA的348个ID及已标注203个ID都出现在其573行全量文件中；573行实际上只有557个唯一ID。它们与3D-Mem/Abstain-A的184题均无共同ID。文件名和README的“test questions”不能代替实际运行划分证据；这不是本轮证明原作者实验泄漏，而是复用时不能把573全量文件直接当与校准独立的测试集。原始文件保持不变，不自行去重/重划分。

## 补充反证及阅读深度

[MemoryEQA，2505.13948](https://arxiv.org/abs/2505.13948)、[Sequential-EQA，2607.21571](https://arxiv.org/abs/2607.21571)：既有笔记/源码契约已说明记忆服务规划/停止、跨题持久化；不能将“增加记忆”当D1差异。本轮没有把未获取的新轨迹/权重或MemoryEQA版本一致性称为已解决。

[CLARA，2306.10376](https://arxiv.org/abs/2306.10376)的原始摘要已描述clear/ambiguous/infeasible命令分类及交互消歧；这是“给不能完成的问题分类、必要时询问”并非新概念的补充反证。仅核摘要/身份，不据此宣称其完整覆盖动作预算取证问题。检索还命中[To Ask or Not to Ask?，WACV 2025](https://openaccess.thecvf.com/content/WACV2025/papers/Abraham_To_Ask_or_Not_to_Ask_Detecting_Absence_of_Information_WACV_2025_paper.pdf)，PDF访问403，未读全文，不用于决定性覆盖判断。

## 剩余差异：只能记为待证实，不能自动升格为创新

**审计者推测。** 仍可提出更严格的问题：在特定prefix、同一状态、已声明动作与剩余预算下，区分“历史已有但中间链丢失”“存在合法取证路径”“需要真实用户意图”“全部合法路径均无足够证据”“尚无证明”。这是**证据与反事实认证层面**的差异，尚无新机制，也没有本轮数据证明其为足量、稳定的实际失败模式。

最有力的否定路线是：先让原记忆可追溯，再比较一次重检索、一次合法重观察、独立阈值校准和APED式观察/澄清决策。如果它们已解决问题，或所谓收益仅来自额外帧/动作/用户答案，则D1不应继续作为方法论文候选。换EQA数据集、重新命名拒答类型、把人工坏前沿标签当可恢复性真值，都不能填补差异。

因此，阶段一“优先讨论D1”的排序缺少这篇直接先行工作和字段核查支撑；本轮撤销其作为已具备方法创新依据的优先推荐。保留严格审计问题，不表示已批准D1进入实验。
