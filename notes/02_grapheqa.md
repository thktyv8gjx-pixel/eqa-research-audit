> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# GraphEQA 精读

核验日：2026-10-21。论文：[arXiv:2412.14480v2](https://arxiv.org/abs/2412.14480v2)，[CoRL 2025记录](https://openreview.net/forum?id=Yy9EVIajH5)。采用[作者发布终稿](https://saumyasaxena.github.io/grapheqa/grapheqa_2025.pdf)，本地 `papers/grapheqa_corl.pdf` 29页；已读p1–9、p19–20，其他附录未全读。

**论文原文——方法与假设。** 用Hydra构建含房间、地点、物体和前沿的3D语义图；文本化图加SigLIP选出的历史视图与当前图像供VLM决定目标及停止。图、深度、位姿和检测质量直接决定输入信息。VLM能对答案作出高置信判断，不等于置信度已经校准（p3–6）。

**论文原文——数据/指标。** HM-EQA及OpenEQA的选择题设定，报告成功率、路径/步数等。p7表1：GPT-4o配置HM-EQA为63.5；p8表2图像单独45.7、图结构单独13.6、组合63.5，支持互补性，但不证明任意3D图都会优于视觉记忆。p19表7附近的开放回答对照与选择题不同；不能拿69.1选择题分数与3D-Mem开放题52.6作排名。部分路径统计只覆盖成功episode，应保留这一分母条件。

**作者自述局限。** p9 §6：闭集检测器、VLM过度/不足自信，以及单层环境。p6报告运行机器为2张TITAN RTX、64GB内存；这不是最低显存需求证明。

**失败证据。** p19附录C.4表6和p20图5–6：未看见锅/灶仍靠常识答对；枕头颜色存在多个视觉上可辩护的答案。前者是“正确但未支持”的假阳性，后者可能是标注/问题歧义，不能都归为导航失败。已查看p19表格渲染；p20图渲染另存 `papers/figures/grapheqa_failure_p20.png`。

**公开性。** [官方仓库](https://github.com/SaumyaSaxena/graph_eqa)，树快照提交 `d3fbbf14bdb05631a1633556d7d3056601374cd3`。有规划器、仿真入口及 `cfg/open-eqa-choices.json`；HM3D资产受原许可限制。OpenReview仅核实投稿/会议信息，未获得可归属该稿的正式评审全文；不能借用ToolEQA评审冒充。

**我的解释。** 有价值的是区分支持证据与正确猜测，并控制模型、选择题选项、停止规则及地图权限后观察失效。更换为图记忆本身已有直接前作；额外给真实平面图也改变了信息权限。相关威胁：[EXPRESS](https://arxiv.org/abs/2503.11117)、[PQB-EQA](https://aclanthology.org/2025.acl-short.11/)、[HFLEX-EQA](https://arxiv.org/abs/2609.26360)。
