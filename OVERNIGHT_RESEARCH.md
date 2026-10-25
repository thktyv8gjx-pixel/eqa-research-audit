# OVERNIGHT_RESEARCH

**2026-10-25｜本轮结论：NOVELTY_OVERLAP（核心通用机制），研究决策 NO_GO（按当前描述作为独立创新立项）。**

候选是：用在线可获取的几何证据，判断竞争三维解释能否被观察区分，进而决定立即回答、继续观察及下一视角。定向反证发现：ATAP 已明确实现“几何多假设—可区分性收益—真实观测验证—停止”的闭环，并报告对应消融。按照本轮“相同机制已有实现与验证就停止”的规则，不再为这一通用机制启动新方法或基线工程。

**判断边界：尚未核实一篇同时满足相同 EQA 任务、相同信息接口、完整相同机制的工作。ATAP 是 RGB-D 任务抓取，不能说它已解决 RGB 空间问答，也不能把多篇论文拼接成一个已存在的完整系统。NO_GO 针对当前机制创新主张，不代表 H1 在 EQA 上为假。** 本轮不凭数据缺失否定科学假设，不将换任务名称自动当作创新。

本文件继续作为唯一研究记录。此前 ArtiPoint 的有条件复现、作者请求草稿及配对分析门，完整保存在 [963737b 版笔记](https://github.com/thktyv8gjx-pixel/eqa-research-audit/blob/963737b736c67ca688ee20f6b7e288b10c160c7d/OVERNIGHT_RESEARCH.md)；其状态不由本轮改判。MoMa-SG、旧下载器和已关闭 EQA 支线均未重启。

## 1. 决定性反证：ATAP 已把可区分性用于真实主动观察

原文：[Imagine then Verify，2609.23504v1，2026-09-20](https://arxiv.org/html/2609.23504)。直接读取 III–V；未找到论文内官方代码入口，未独立复现。

ATAP 的输入为已采集 RGB-D、标定/位姿及任务指令。IV-B 保留多种完成几何的配准，生成结果仅为待验证先验。IV-C 公式7–8计算预期验证量，9–11计算假设区分与后验熵，12联合区分/验证/移动代价选视点，14同时约束剩余未验证量和假设熵以停止观察、执行抓取。GT几何供离线评分。

作者表II：85个高遮挡仿真场景，单假设→完整方法的功能成功率 **48.24%→56.47%**，平均调整 **3.14→2.51**；最大预算均为5。表III另有真机验证。它支持“通用机制已有实验先例”，不等于同信息EQA已解决。

反证限制：单假设消融同时改变假设表示与规划，不能单独识别熵项相对可见性项的因果贡献；同一最大预算也不等于同一实际观察数。因此不能据此宣布本任务H0a/H0b已排除，但“首次用竞争几何解释区分能力进行主动观察”不能成立。

## 2. 指定五项工作的逐项对照

“未见显式区分量”限于已读方法、附录及下列源码，不是宣称其所有后续版本都不存在该机制。数字分别属于作者自己的协议，不横向拼成方法增益。

| 工作与原文位置 | 真实任务、输入输出 | 几何区分及回答/拒答/下一视角 | 信息边界与决定性证据 |
| --- | --- | --- | --- |
| [SpatialUncertain v2](https://arxiv.org/html/2605.30557v2)，§3.3–3.4、表1、附录A.2.2/A.3.2 | 受控渲染 RGB 空间问答；输出关系答案或 Cannot determine。ViewSel 另从五个候选图像选择参考视图；AbstainViewSel 先答或拒答，再进行选择。 | 联合任务接口已存在；未见由竞争三维假设构成的几何区分评分。 | 五幅候选图像在选择时已呈现，不是仅凭当前视图预测未知下一观察。场景几何、隐藏遮挡物后的参考 mask、物理尺寸供构造标签/分组；不能当部署输入。§3.3 明说透视冲突不必然意味着单图不可恢复。表1 GPT-5.4 的 ViewSel 70.9、AbstainViewSel 28.5；两者定义不同，不能相减成配对因果效应。 |
| [CoV，ACL 2026](https://aclanthology.org/2026.findings-acl.1623/)；[可读 arXiv v2](https://arxiv.org/html/2601.05172)，§3、表2–3、附录A | 问题、已有帧及预建三维场景→选锚点、相机移动/旋转、最终文本答案。 | 已有回答—继续看—选动作；以 VLM 指令与充分性判断控制，未见显式几何多假设区分评分或独立拒答风险控制。 | 原任务允许全场景重建、全局 BEV 和新视图渲染；对未知环境的部分观测协议属于额外信息，不能直接作为同信息对照。表3检验粗选帧，表2增加最低动作步数，不能证明固定观察预算下的 H1。 |
| [Opti3D，IEEE Access 2026](https://doi.org/10.1109/ACCESS.2026.3720265)；[同 DOI 作者稿全文](https://www.researchgate.net/publication/411278767_Query-Driven_Evidence_Retrieval_for_Efficient_3D_Question_Answering)，III-C/算法1、表4–8 | 问题、既有多帧、相机参数及三维点云→BEV与去重后的局部证据→冻结 Video LLM 答案。 | 射线几何一致性合并实例；再用检测置信度、中心性、面积及边界惩罚评分。未形成竞争场景假设下的观察可区分性，也不控制在线停止/拒答。 | 使用已有场景及候选帧做离线证据检索。算法1及表5已经覆盖几何去重收益；表6分析视图评分权重。不能把“几何帮助筛图”当新贡献。出版网页直接读取受验证码限制，方法/实验依据为同 DOI 作者稿；未找到可核官方代码入口。 |
| [AVIC v2](https://arxiv.org/html/2602.08236v2)，§4、公式1–4、表4 | 当前图像、问题和选项→skip/call_wm、动作计划、世界模型生成视图及最终答案；另有导航扩展。 | 已联合决定是否追加观察、计划和预算；多数票门控与轨迹验证器评估生成结果。未见物理多假设似然的显式计算。没有独立的最终拒答保证。 | 新视图是世界模型生成，不能等同已获取的真实视觉证据；训练奖励可用答案 GT，推理不因此获得 GT。表4只门控为73.3，门控加动作控制为79.3，提示简单开关已不足。 |
| [E3VS-Bench v3](https://arxiv.org/html/2604.17969v3)，§3–5、表2–5及补充协议；[官方 README](https://github.com/K0uya/E3VS-BENCH) | 当前 RGB、问题、位姿/碰撞反馈→5-DoF 离散动作或 stop→最终回答。 | 已评测闭环观察与停止；默认代理无显式几何假设区分，配置默认不加入 Cannot answer。 | 场景供环境渲染；GOAL图像与 GT 答案给离线 judge，不能给策略。表3 Start/Goal 差距是特权视角对照，不是选视角方法收益。代码发布 QA/位姿；图片因 ScanNet++ 条款不重分发，重渲染需 CUDA 栈。 |

### 已实际读取的关键源码与固定版本

- SpatialUncertain：[`420c8700d487893ac17c47044abf8287b05240f8`](https://github.com/zhangyuejoslin/SpatialUncertain_code/tree/420c8700d487893ac17c47044abf8287b05240f8)。读取 `eval_gpt5.py`、`gen_distortion_scene.py`、`render_distortion.py`、`generate_questions/question_gen_distortion.py`。其中 [`build_prompt` L617–683](https://github.com/zhangyuejoslin/SpatialUncertain_code/blob/420c8700d487893ac17c47044abf8287b05240f8/eval_gpt5.py#L617) 使用图像/问题/选项并允许 Cannot determine；不是几何检验器。仓库有生成/渲染源码，但完整树中没有已渲染题目资源，也未核到 v2 两阶段 ViewSel 的专门执行入口，不能冒称完整协议已经可运行。
- CoV：[`c41fd1997e21fd58abc86f93f2cad83ea3d56ba4`](https://github.com/ziplab/CoV/tree/c41fd1997e21fd58abc86f93f2cad83ea3d56ba4)。读 `cov/agents.py`、`bots.py`、`camera.py` 与 `prompts/chatbot.j2`。[`cov_agent`](https://github.com/ziplab/CoV/blob/c41fd1997e21fd58abc86f93f2cad83ea3d56ba4/cov/agents.py) 加载 GLB、渲染 BEV、调用相机指令，遇 done 提取答案；提示还强制最低动作数。GT 答案在该函数仅加入记录页面，未据此指控答案泄漏。
- AVIC：[`40ffc1c52450dcbdea9cf16e21226eeb6be7cbbe`](https://github.com/Yui010206/Adaptive-Visual-Imagination-Control/tree/40ffc1c52450dcbdea9cf16e21226eeb6be7cbbe)。[`pipeline_avic.py` L333–379](https://github.com/Yui010206/Adaptive-Visual-Imagination-Control/blob/40ffc1c52450dcbdea9cf16e21226eeb6be7cbbe/visual_spatial_reasoning/pipelines/pipeline_avic.py#L333) 的 `_majority_vote_decision` 和 `_score_one_candidate_ordered` 分别统计策略票、用 VLM 为整段生成轨迹评分；读了对应 prompt，不把语言里的“解决歧义”当成可执行的几何证明。
- E3VS：[`bb7e603ccdcf2dd77fbeedd15660a09310a8a881`](https://github.com/K0uya/E3VS-BENCH/tree/bb7e603ccdcf2dd77fbeedd15660a09310a8a881)。读取 `e3vs/agents/base_agent.py` 和动作提示；[`DEFAULT_CONFIG` L32–65](https://github.com/K0uya/E3VS-BENCH/blob/bb7e603ccdcf2dd77fbeedd15660a09310a8a881/e3vs/agents/base_agent.py#L32) 明确 stop 及默认关闭 Cannot answer。未运行代理或评测器。

## 3. 截至 2026-10-25 的额外直接反证

- **[RFL，2610.11039v1，2026-10-08](https://arxiv.org/html/2610.11039)**：IV-A–D，公式1–6；训练 teacher 从全场景渲染一/二步未来视图，student 推理只用问题、已观测 RGB 历史和候选动作，预测未来可回答性。不能把训练特权与部署泄漏混同。表I同主干与停止机制下均分2.14→3.05，已覆盖部署时不渲染未来视图的 question-guided 选视角；它预测的是 VLM answerability，不是物理几何可辨识性证书。
- **[FOVEA / S-BOED，2605.01345v3](https://arxiv.org/html/2605.01345v3)**：§2–4、公式4及附录算法。已将视觉取证写成对隐变量的预期信息增益与序贯设计，实际方法用覆盖率—分辨率及 VLM 可解性代理优化图像裁剪；不是三维相机的同协议实验，但“根据假设不确定性选下一证据”这一通用表述也不是新理论。
- **[Explore until Confident](https://arxiv.org/html/2403.15941)**：§V、停止策略实验，以校准的可能答案集合及其跨步更新决定停止，探索使用在线深度语义地图。此为停止决策的直接基础对照，不是几何可行场景集合；也不能无视它而只比未校准单阈值。

以上不以综述摘要代替原文。未对上述不同模型、任务、信息预算的数值做跨论文排名；表内数字仅标明哪些机制已有作者实验支持。

## 4. 真实运行与数据准入事实

**真实模型推理0次、真实样本实验0题、新方法代码0、安装0。** 因新颖性门未通过，未启动第二、三阶段；不存在可交付的逐题原始预测或方法增益，不编造空结果表。

另已只读核实官方数据入口，不能把“公开页面”当成“已取得完整样本”：

- [SpatialUncertain 官方 HF 数据卡](https://huggingface.co/datasets/Yuezhangjoslin/spatialuncertain) 标注 CC-BY-4.0，但访问文件需登录、接受信息共享条件并获得权限。卡片声明多视角 PNG、相机参数、对象/场景标注；未实际取得它们，不认证其内容完整性或与 v2 划分一一对应。
- 本机检查只返回凭据是否存在，未读取/输出任何秘密；未发现 HF 环境凭据或默认 token 文件。对卡片列出的 `questions/perspective_benchmark.json` 仅发起一次 HEAD，真实响应为 **HTTP 401 / GatedRepo**，要求已获授权并认证。未自动接受条款、未绕过访问控制、未重试下载。
- README 另链 Google Drive 场景目录，本次工具无法读取；未据此宣称文件不存在。获取 QA 元数据也不能代替初始 RGB、全部候选视图和逐视图位姿。对完整样本的资源门而言，唯一已证实的决定性缺口是**尚未取得合法授权且完整的样本包**；不把潜在模型/环境困难再列成已发生的阻塞。

这个访问缺口不是 NO_GO 的科学依据；即使立即拿到数据，也不能恢复被现有机制反证的“首创”主张。

在线与 oracle 边界：允许给策略的几何必须来源于截至当前的实际传感器观测、已知标定与在线位姿/估计；对象真实尺寸、隐藏结构、全场景 GT、未来候选图像、评测 GOAL 与 GT 答案只能按原协议用于离线评价或单列 oracle 上界。候选图像已经全部展示的 ViewSel 与尚未访问视点的在线 NBV 是不同信息问题，不能直接比较为策略收益。

## 5. 科学判断、停止范围与导师讨论

- **创新性：** 任务层已有 SpatialUncertain 联合接口、CoV/E3VS 的动作—停止闭环；几何证据组织已有 Opti3D；竞争三维假设区分并经真实观测验证、联合停止已有 ATAP。当前未提出超过这些已实现机制的可操作差异，不能以移植到 EQA 自动建立创新。
- **H1：** 未在本任务上检验，不能说被证实或被否定。ATAP 只提供跨任务的机制先例；它不是同信息 EQA 上的完整替代。
- **H0a / H0b：** 未排除。尤其需要区分多假设数量、可见性收益和信息增益项，匹配实际观察次数而不只是上限；本轮不以文献总体增益替代这些对照。
- **H0c：** 通用机制重合已有直接证据；完整同任务同信息系统的等价性未证实。依用户预设止损，**当前 Idea 作为独立机制创新 NO_GO，停止此路线的新方法/基线投入，不改名保留、不转选其他方向。**

**可交给导师的具体讨论，仅基于已有作者实验：** ATAP 表II是否足以支持“多假设规划有用”，却仍不能回答“额外价值来自假设区分项还是不同假设下的预期可见性”？其消融同时改了表示与评分，故后一个因果问题仍未被隔离。这个实验解释边界值得讨论，但不是本轮已发现的新 EQA 机制，也不作为继续立项的借口。本轮没有自有真实错例，暂不提出新的算法题目。

本轮只更新本文件并保存原创分析到已有 GitHub 仓库；论文、第三方源码和数据均未另存/上传。没有新候选缓存需要清理；已有唯一资料、未跟踪用户文件及历史阶段记录保留。最终提交及远端原文校验结果随交付给出。
