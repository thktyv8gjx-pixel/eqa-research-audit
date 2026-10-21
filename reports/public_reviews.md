> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# 公开评审：已读原文与获取边界

核验日2026-10-21。只把标为Official_Review且能对应forum的记录当正式评审；作者回复、投稿摘要、检索词碰巧命中、HTTP200验证页都不等于评审。原始响应保存在 `papers/sources/reviews_*.json`；[解析索引](../SOURCE_INDEX.json)可能包含无关搜索命中，必须按下表forum过滤。

## 确实读到的相关正式评审

| 对象与身份 | 主要质疑（转述） | 对本项目的意义与版本边界 |
|---|---|---|
| [SnapMem，ICLR 2025撤回投稿](https://openreview.net/forum?id=mz8unSsSsB)，[评审ZB2d7PiKqU](https://openreview.net/forum?id=mz8unSsSsB&noteId=ZB2d7PiKqU) | 已知位姿/物体坐标是强条件；按检测物体选快照会漏掉无检出物体区域；规则/超参数跨环境泛化证据不足；缺2D/拓扑记忆近邻 | 与3D-Mem作者列表、方法高度重合，作为**同作者相关投稿**使用；没有逐版比对证明等同CVPR终稿，更不是CVPR官方审稿。准确位姿、漏检问题在后续3D-Mem局限中仍明确存在 |
| 同一SnapMem投稿，[评审JY59MObHDl](https://openreview.net/forum?id=mz8unSsSsB&noteId=JY59MObHDl) | 创新差异不清；缺prefilter前后图像量与消融；缺杂乱/光照等细化失败分析；只用GPT-4o限制复用 | 3D-Mem当前全文已有相关消融、失败图、开放VLM的其他任务实验，**这些批评已部分回应**；不能把旧评审逐条当作当前仍未解决事实。也不把“必须使用更复杂学习方法”当科研定律 |
| [ToolEQA / EQA-RT相关投稿](https://openreview.net/forum?id=lHfUG7iFaJ)，[评审o7tmGdDbBj](https://openreview.net/forum?id=lHfUG7iFaJ&noteId=o7tmGdDbBj) | 缺同pipeline去工具对照，难区分多步分解与工具收益；效率与答案召回混合；微调/零样本配置不明；全局图权限和动作粒度不同；未见场景目标数更少可能混淆泛化；工具/提示词细节不足 | 这是**近邻方法的评审，不是GraphEQA评审**。直接转化为本轮设计要求：同VLM/输入权限/动作接口；拆开效用与成本；按目标数分层；保留简单消融。没有核对所有作者回复及最终修订，故只陈述该轮评审提出过的质疑 |

前两条来自[reviews_memory_search.json](https://api2.openreview.net/notes/search?term=Memory-Centric%20Embodied&limit=50)；第三条来自[reviews_grapheqa_search.json](https://api2.openreview.net/notes/search?term=GraphEQA&limit=10)。搜索文件名只是查询入口，**不能决定评审归属**。

## 八篇精读及其他候选的检索状态

| 论文 | 状态 |
|---|---|
| GraphEQA：[Yy9EVIajH5](https://openreview.net/forum?id=Yy9EVIajH5) | 核实CoRL 2025记录；直接API返回验证HTML，搜索响应未获得可归属的正式评审全文。记“未读到”，不记“无质疑” |
| 3D-Mem | 见上方同作者SnapMem相关稿，不能把撤回投稿写成ICLR录用，也不冒称CVPR审稿档案 |
| MemoryEQA、EXPRESS、AbstainEQA、StreamEQA、PQB-EQA、Sequential-EQA | 未取得可确认对应版本的公开正式评审全文；不推断会议必然不公开或不存在评审 |
| ActionEQA：[HY2ruqdMt4](https://openreview.net/forum?id=HY2ruqdMt4) | 有Accepted投稿记录和5条Official_Comment响应；搜索所获不是完整Official_Review集合，不将作者答复改写为评审原话 |
| Prune-Then-Plan：[oo7IphaRhx](https://openreview.net/forum?id=oo7IphaRhx) | 核实对应投稿命中；未取得完整评审集合。不从OpenReview投稿状态推断最终CVPR录用；作者项目页单列为作者声明 |

本轮没有绕过验证、登录或付费获取评审。读取标准公共搜索端点得到的JSON仍需查身份；多条不同论文用同名“3D-Mem”时，只采用空间场景记忆这篇的来源。

**我的解释。** 反复出现的审稿风险是：信息/预算不对等、机制贡献未隔离、任务难度组成混淆、代码版本与评测细节不清。它们比“再堆一个模块”更应先排除；任何新候选也不能仅用评审意见代替当前原文和实测证据。
