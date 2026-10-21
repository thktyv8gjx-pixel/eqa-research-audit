> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# Sequential-EQA 精读

核验日：2026-10-21。[arXiv:2607.21571](https://arxiv.org/abs/2607.21571)，IROS 2026为作者项目/仓库声明，本轮未另核IEEE录用记录。采用[作者PDF](https://sequential-eqa.github.io/paper.pdf)，本地 `papers/sequential_project.pdf` 8页；正文p1–7已读，p8参考文献未逐条读。

**论文原文——问题/协议。** 每题重置记忆掩盖长期场景经验收益。50个OpenEQA/HM3D场景、498题，按场景形成固定seed随机序列；冻结权重；题间恢复规定初始位姿，保留模型许可的场景记忆，重置问题目标/动作队列/停止状态（p3–5）。主要协议不截断/总结记忆。泛泛“跨题共享记忆”已被直接覆盖。

**指标与结果。** SR、路径长度PL、Memory Advantage MA（SR差，百分点）、Spatial Advantage SA（路径的归一化减少）。p5表II：3D-Mem 25.5→58.8，MA=33.3个百分点；MemoryEQA 61.0→62.4，MA=1.4个百分点。相对增益大的模型不等于绝对分最高；不能按MA单独选最好baseline。p5写A5000/Qwen3-VL-8B量化配置，但本轮未验证可迁移到8GB。

**作者自述范围/局限。** 无独立Limitations节；p7真实机器人测试规模小，ExploreEQA的33→26等差异作者明确提示小样本谨慎。p5–6后期题号只含足够长的场景序列，作者已说明条件分母；不能把题号上升曲线直接解释为排除场景差异后的记忆因果收益。

**失败证据。** p6图5：情景模式把烟雾探测器位置答成衣帽间；序列模式借已有空间经历答对，示例从1/3变3/3。它是作者选择的案例，未证明所有困难题均得到改善，也未测定有界记忆的跨题干扰曲线。

**静态代码审查。** [仓库](https://github.com/jangablox/sequential-eqa)，有benchmark/、evaluation/、adapter/实现及数据构造记录。`adapters/README.md` 明确不同模型保留的状态；`configs/upstreams.yaml` 记录开发时上游commit。setup脚本说明会拉当前默认分支：复现时需要另外固定commit，不能把记录的commit视为运行时已强制锁定。MemoryEQA对应本轮快照提交。未克隆/执行整套上游环境。

**我的解释。** 有限容量下何时应忘、忘后错因与跨问题证据身份绑定可作条件候选；必须超出本文无截断设定，同时对照[MemoryEQA](https://arxiv.org/abs/2505.13948)、[HIMM](https://arxiv.org/abs/2602.15513)、[Embodied VideoAgent](https://arxiv.org/abs/2501.00358)。压力测试应固定原始顺序/初始位姿作主结果；新增顺序扰动只作为单独登记的诊断，不能改官方划分。

**新增源码证据——序列来源缺口。** `benchmark/README.md` 明确说发布序列是canonical artifact，但原始源数据版本和生成seed未保留，应记unavailable。故上文“固定seed随机顺序”是论文描述，**不能声称已拿到生成该序列的seed**。下一阶段应直接冻结发布序列及其hash，先核对50场景/498题和pose字段，不自行重新shuffle来“复现原划分”。
