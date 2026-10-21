> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# PQB-EQA 精读

核验日：2026-10-21。论文：[Grounded, or a Good Guesser?，ACL 2025短文](https://aclanthology.org/2025.acl-short.11/)；非arXiv条目以正式URL为标识。`papers/pqb.pdf` 12页，已读正文PDF p1–5（印刷页124–128），附录实现/调查细节未全部精读。

**原文——问题/机制。** 同一个问题放到至少两个答案不同的Minecraft环境，按问题平衡答案，使只依赖语言先验的策略不能轻易超过机会水平（p1–3）。不是给模型加一个模块，而是检验视觉证据的贡献。

**数据/假设。** 424个question–environment–answer元组、31个环境；人类探索产生截图（1Hz）及操作记录（20Hz）。二选一评测，环境非照片级，和HM3D开放回答设定不同（p2–4）。[正式数据DOI](https://doi.org/10.5281/zenodo.16112260)已从作者项目页解析，并核对Zenodo/DataCite元数据；未下载压缩包。

**指标和实验支持。** p4表1：盲GPT-4o 50.7%，提供oracle截图82.7%。主要实验使用**oracle动作/截图选择**，不是一个学习到的探索策略取得82.7%。残留错误说明视觉输入仍不够保证正确，但不能从17.3%的错误反推全是导航或记忆故障。

**作者自述局限。** PDF p5 §9（印刷128）：oracle行动、二选一而非自由回答、英语、非照片级Minecraft场景、适用于评价而非大规模训练。没有逐例模型错误归因可复用，未提供主动EQA策略的完整失效分类。

**代码/数据。** [生成工具](https://github.com/MilesShelton/pqb_eqa)，有 `generate_environments.py` 等及地图结构；[修改版MineRL](https://github.com/finegan-dollak/mineRL-pqb-eqa)。README本身仍有下载链接占位，但[作者项目页](https://milesshelton.github.io/pqb_eqa/)的DOI已真实解析，不能只凭README误判无发布。实际运行还涉及Minecraft账户/版本，不假定用户拥有。

**我的解释。** “同问异景排除盲猜”已被该文提出，应作为所有候选的诊断控制，不能包装成新题。若迁移到跨题记忆或拒答，需要证明评价了不同能力，并对照[AbstainEQA](https://arxiv.org/abs/2512.04597)的同问视觉条件失败例。构造任务也不能仅改答案而不验证视觉上可辨别。
