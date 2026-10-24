# OVERNIGHT_RESEARCH

**NO_GO（本轮论文研究准入）。三个独立方向已完成实质筛选；没有找到同时具有机制特异的失败证据、足够近邻差异与可执行最小验证的论文候选。** 最值得带给颜老师讨论的是 ArtiPoint 的“真值交互边界反而降低旋转轴精度”现象，但只建议讨论一次有界因果诊断，**不建议据此启动新算法研发**。没有把缺 CUDA、一次网络超时或缺数据单独当作科学反证。

2026-10-25，Asia/Shanghai。遵循本次三轮目标；`d9324db` 只是[首批记录](https://github.com/thktyv8gjx-pixel/eqa-research-audit/blob/d9324db1f2718af30c7891371ae3161a84cea78b/OVERNIGHT_RESEARCH.md)，不是整个任务的终点。其来源、CPU 表格核算和未运行记录继续保留在 Git 历史，不重复执行。D1/D2/D3、RoboSpatial Z 原点及 inside/under 宽泛提案均未重启。本文件是本轮唯一维护的报告。

## 一、三轮实际筛选与科学判断

“未准入”表示目前不值得按该主张立项，不表示论文方法无效，也不表示假设已被实验否定。每轮不超过三篇主候选；用于反证的近邻未另列为实现候选。

### 第一轮：操作失败检测与目标完成验证

| 主候选、公开算法 | 决定性内容与判断 |
| --- | --- |
| [I-FailSense，ICRA 2026 / v2](https://arxiv.org/html/2509.16072v2)；[官方 0c71f56](https://github.com/clemgris/I-FailSense/tree/0c71f564cece59816733a8d9ac58ee62b264bf8c) | 延续已核实线索：DROID 负例生成把下一组 task 移给当前轨迹，却不在该函数中验证目标确实未实现。仍没有真实矛盾标签样本。RoboReward 已有反事实标签复核，RoboRMBench 已研究目标同义性；“增加去重/清洗”不是独立方法贡献。**当前负例污染提案未准入，不能把源码少检查当成已观察到污染。** |
| [Robometer，RSS 2026 / v2](https://arxiv.org/html/2603.02115v2)；[官方 352d160](https://github.com/robometer/robometer/tree/352d160389daa964788de1ec933d1925f3a6de4f) | 联合帧级进度/成功与轨迹偏好。§V 承认稀有失败、长历史、不可见接触状态仍困难；B-2 以数据源统一完成比例修正时间标签。读了 `samplers/base.py`、`progress.py`、`pref.py` 与 `datasets/helpers.py`：标签依赖帧索引和 cutoff，不能自动等同物理完成。但这一问题已有 SARM 阶段标注及 RynnValue 时序捷径控制直接覆盖。**不以“时间进度有偏”重新立题。** |
| [SARM，ICLR 2026 / v2](https://arxiv.org/html/2509.25358v2)；[官方 opensarm 9978198](https://github.com/xdofai/opensarm/tree/9978198d4c6601f34063fa40e63f9ddc5baf7f68) | §3.1 明确处理同状态因示范时长不同而得到不同进度的问题。读了 `models/stage_estimator.py`、`subtask_estimator.py`、`workspace/sarm_ws.py`。作者不仅加入阶段标注，还用 rewind；附录已展示真实回退、误抓和“假完成”的对照。单一 dense 模型在真实 rollout 较差，也已有消融解释；后续 SARM2 扩展多任务。**泛称阶段/记忆/回退改进没有剩余差异。** |

最强反证链：[RoboReward §4.2/A.2.3/A.3](https://arxiv.org/html/2601.00675v2) 已验证反事实标签；[SARM §3.1/4.1](https://arxiv.org/html/2509.25358v2) 已处理进度标签不一致；[RynnValue §3.2](https://arxiv.org/html/2608.09853v1) 已针对采样顺序和跨查询外推捷径设计干预。另有 [FailBench §4.2/B.1](https://arxiv.org/html/2609.03611v1) 直接研究检测器跨源退化和类别偏置。因此，“专用检测器会失效”或“换更好进度信号”都不足以形成新的科学问题。

资源与科学门分开：当前没有相应可运行模型或真实负例配对；不重试上一轮 DROID 地址。Robometer 官方 Git 树确有三个很小的示例视频及缓存奖励数组，**没有下载**：它们缺少当前假设需要的逐帧完成真值/反事实目标，读取它们只为增加运行计数没有判别力。完整模型不是本轮必须准备的工程任务。

### 第二轮：主动感知与操作决策

| 主候选、公开算法 | 决定性内容与判断 |
| --- | --- |
| [Vision in Action，CoRL 2025](https://arxiv.org/html/2506.15666)；[官方 1588edb](https://github.com/haoyu-x/vision-in-action/tree/1588edb2ed4e4fb8f19562d3a36e4e8cb993b4e5) | 联合学习头部与双臂动作；作者报告增加腕部视角后平均下降 18.33%，并明确不支持搜索记忆。这里是可研究的真实局限，但“加视角/加记忆”已有明确结果和后续，不是本项目的新机制。 |
| [Act, Sense, Act / CoMe-VLA，2026-07 v2](https://arxiv.org/html/2602.04600v2)；[官方 786d59c](https://github.com/Joringell/ASA/tree/786d59cd84af08470eafc68445dddd32af7153fa) | 唯一深入对象：认知头控制探索与操作切换。§5.1把标签解释为信息已充分，但公开数据处理监督 `current/complete`；读了 data processor、TaskStateHead、focal loss 和 sigmoid 返回。提出“信息充分是否混同阶段完成”的待检验解释，**没有把它当成已证实失效**。 |
| [ActiveArena，2026-09 v2](https://arxiv.org/html/2609.24124v2)；[官方评估 1bf2c77](https://github.com/leeibo/ActiveArena/tree/1bf2c77b8d3ab978fc5b4599a69d017f593edbe8)、[VLA abaea42](https://github.com/leeibo/ActiveArena-VLA/tree/abaea42b223d40f7b763cd879ce926c8c0c906a1) | §4.3 已实测预测依赖的稀疏触发会错过记忆写入时机，比较周期采样、阶段监督、记忆和独立规划器。核心部署代码有阶段变化写入及历史选择。**“更可靠的阶段触发/记忆写入”已有直接邻居。** |

对 CoMe-VLA 的关键反证：
- [§6.6](https://arxiv.org/html/2602.04600v2) 已做 10 分钟目标消失/移位测试，禁用抓取，报告持续搜索、再锁定和恢复搜索。这削弱了“末尾监督必然学成倒计时”的推论。
- Table 5 的 83.3% 对 22.7% 不能隔离信息充分性头：§12.1.1 的消融同时替换整任务指令并禁用切换。
- [官方 README](https://github.com/Joringell/ASA/blob/786d59cd84af08470eafc68445dddd32af7153fa/README.md) 未公开完整推理/部署代码；已核到分数返回，未声称核到真实切换闭环。标签时间窗还涉及末尾扩展，未用局部公式差异宣布协议错误。

最强三个近邻：[ActiveArena §4.3–4.5](https://arxiv.org/html/2609.24124v2) 已比较阶段与周期写入；[SaPaVe，CVPR 2026](https://arxiv.org/html/2603.12193) 已解耦相机/操作并重搜目标；[Gaze-Guided Task Decomposition，IROS 2025，§IV-D](https://arxiv.org/html/2501.15071) 已报告真实 MoveFlask 示范 1/106：抓住瓶子前就看向目的地，造成分段错误。因而“提前看不等于当前动作完成”本身不是新发现。

本方向未准入的科学理由是：没有机制特异的真实失败，消融不能识别所提原因，且宽泛改法已有直接覆盖。ASA 的小型缓存认知分数未取得，网页及一次小目录请求未成功；这只是额外资源门，**不是上述科学判断的依据**。未假定 GazeTaskDecomp 的公开示范一定含那条失败。

### 第三轮：空间表示与物理交互

| 主筛选入口、公开算法 | 判断与边界 |
| --- | --- |
| [CCA，T-RO 2025](https://ieeexplore.ieee.org/document/11049010)；[官方 76b6d6e](https://github.com/UTNuclearRoboticsPublic/closed-chain-affordance/tree/76b6d6e8f8086657974c92200f152a2f917a6410) | C++ 闭链规划实现公开。关节轴、接触和目标是输入，不把缺视觉模块说成方法错误。未取得全文具体失败证据，止于入口筛查；**不借它否定该研究方向**。 |
| [IAAO，CVPR 2025](https://arxiv.org/html/2504.06827)；[官方 5b24d6e](https://github.com/lulusindazc/IAAO/tree/5b24d6e86dbcc6652c937e6f7cba2a1004a84023) | 实质特征场、跨状态匹配与融合算法存在；两状态多视图和刚性部件是任务设定。公开依赖中存在空文件，完整复现未验证；此为资源边界。泛称加三维/语义/关节约束没有独立主张，未据此制造新提案。 |
| [ArtiPoint，CoRL 2025](https://proceedings.mlr.press/v305/werby25a.html)；[官方 ec88e43](https://github.com/robot-learning-freiburg/artipoint/tree/ec88e43e178616697fbc948d0fdda48c0c880702) | 深入母论文、补充、前端、逐点平滑、可见点配对与关节后端。找到了作者明确未解释的反常消融；下面给出唯一保留的诊断问题。 |

## 二、唯一值得带给颜老师讨论的问题：ArtiPoint 边界负收益

**问题：为什么更准确的人类交互边界不一定带来更准确的关节轴？能否把前端样本变化、运动可辨识性与平滑边界效应分开？**

原文证据固定为[arXiv:2509.01708v1，S.1.3/Table S.2](https://arxiv.org/html/2509.01708#A1.SS3)：GT segments 下旋转轴角误差 **17.14→20.24°**，而平移轴角误差 **14.54→11.99°**；作者写 “not allowing a clear interpretation”。这是作者结果，**不是本轮复现**。反证也必须保留：同版 Table 3 中去平滑反而使旋转轴误差 **17.14→19.38°**，不能说平滑普遍有害。不混用数值不同的旧 OpenReview 版本；正式发表页确认 CoRL 2025，本文数字严格引用上述可读取的 v1。

源码支持的范围：
1. [artipoint.py L522–606](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L522)：GT 区间在 query 选择、tracker、深度投影之前确定。换区间会改变前端上下文和点集，不只是改变轴拟合窗口。
2. [L274–291](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L274)：逐点可见性与手部遮挡、有效深度相交。[L743–801](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L743) 在每段内平滑后拟合。
3. [arti_estimator.py L516–620](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/arti_estimator.py#L516)：求解 `(V + λvel Lvel + λjerk Ljerk) P' = V P`。按点分块，不同可见性会产生不同滤波算子；此处没有跨点刚性项，后端另有共享关节约束。
4. [L167–195](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/arti_estimator.py#L167) 取最早共同可见帧构造点对；论文 S.1.1 又按区间 IoU>0.5 匹配。Table S.2 没有证明两条件使用相同交互/点集，故均值差不是配对机制证据。

**待证伪假设 H：** 固定真实原始点轨迹 X、可见性 M 和 query 身份后，先截窗再逐点平滑与先平滑再截窗，会因可见性异质性破坏跨点刚性，造成旋转轴偏差。

这是源码推导出的解释，**没有真实因果验证**。更简单的竞争解释包括：前端点集变了、匹配交互集合变了、旋转范围变小、共视数下降、深度质量差，或普通有限窗口正则化效应。没有排除它们前，不谈新机制。

## 三、最强三个直接后续与创新否定

| 近邻 | 已覆盖什么；为何不能直接立项 |
| --- | --- |
| [MoMa-SG，2026，§3.2](https://arxiv.org/html/2602.16356#S3.SS2)；[官方 fc4a417](https://github.com/robot-learning-freiburg/MoMa-SG/tree/fc4a417e1859f84ace1dde3f4d6f71ce45e9e569) | 继承轨迹平滑，随后做 arc-fit、rigidity DBSCAN 及 twist 正则。已读 [filtering.py L53–119](https://github.com/robot-learning-freiburg/MoMa-SG/blob/fc4a417e1859f84ace1dde3f4d6f71ce45e9e569/moma_sg/articulation/filtering.py#L53) 与 [L787–830](https://github.com/robot-learning-freiburg/MoMa-SG/blob/fc4a417e1859f84ace1dde3f4d6f71ce45e9e569/moma_sg/articulation/filtering.py#L787)：已用共同可见帧的点间距离变化过滤不刚性。只展示平滑后非刚性不够新。 |
| [PAWS，2026-03，§3.1–3.2/App A.2](https://arxiv.org/html/2603.25539) | 已用接触过滤、OU/RTS 轨迹平滑、全局视角与静态几何轴先验；不等同于逐点滤波，但排除了“加接触/几何先验就是创新”。公开算法/数据入口仍有限，不冒称可运行基线。 |
| [Articulation in Prime，2026-05，§3 Eq.18](https://arxiv.org/html/2605.18645#S3) | 已联合形状与关节拟合，并直接平滑关节量 θ；“改成关节空间平滑”已有明确方法先例。代码尚未核实可用，不以此否定其方法贡献。 |

因此，截窗/缺失观测的非交换性本身是预期滤波效应，刚性或关节空间拟合也已有先例。**当前剩下的是因果解释价值，不是有充分新颖性依据的新算法。** 如果仅证明已知替代能修复流程，结论应是复现/评测解释，而不是论文创新。只有同等运动激励与观测质量下、跨场景稳定存在、强已有对照仍不能解释的机制，才值得重新评估科研准入；本轮没有这类证据。

## 四、下一步唯一最低成本验证（条件性，不启动工程）

仅当合法且完整的真实小缓存已到手，固定最多 3 个独立场景、12 次交互的同一 `X/M/query`、GT 轴、相机姿态、GT/预测窗口及全部失败；不得按结果挑轨迹。

在共同真实帧上比较 **crop-before-smooth、full-smooth-then-crop、no-smooth**。先控制交互配对、旋转激励、共视数和深度质量，再看点间距漂移是否与轴误差变化一致；强对照为已有 rigidity 过滤与原始点直接关节拟合。共享可见帧也须作为简单解释检查，不能只挑最有利平滑条件。

第一步 CPU 诊断只需判断刚性变化；完整轴误差仍须相符的官方后端或作者缓存结果，不能用自建拟合冒称原方法复现。若不存在配对反常，或无平滑/共享可见帧/rigidity 过滤/标准关节拟合/更大运动激励足以解释，则**关闭算法题**。即使发现误差，也先判断是已有方法能解释的流程效应。

官方仓库没有核实到可直接取用的真实 tracks/visibility/GTjoint 小包；README 主要提供整场景 raw ZIP 与相机姿态包。不是“数据不存在”，而是所需小缓存未发布/未取得。可供导师决定是否索取合法缓存；**本轮未联系作者、未下载整包、未启动前端网络或新环境。**

## 五、实际实验、资源与归档

| 项目 | 本轮真实状态 |
| --- | --- |
| 新真实样本 / 模型推理 / 作者性能复现 / 真实轨迹实验 | **0 / 0 / 0 / 0** |
| 旧 CPU 结果 | d9324db 的 I-FailSense 表 II 算术核算保留，未重跑；不能算本轮新实验。 |
| 现成 CPU 条件 | 只读检查 q2_overnight Python 3.12.14：可定位 NumPy/SciPy；未找到 GTSAM、Open3D、Torch。仅用于评估小型线性代数可行性，不声称官方后端已运行。 |
| 安装 / 大型模型数据 / GPU / 付费 API / 真机仿真 | **均为 0**。没有以模拟或 mock 输入制造结果。 |
| 本轮文件与清理 | 仅本文件更新。没有候选专属媒体、缓存、源码副本落盘；删除 0 文件，释放 0 字节。原有唯一资料、环境和未跟踪用户文件全部保留。 |

归档基线 `d9324db1f2718af30c7891371ae3161a84cea78b`。只提交本文件，核对远端 main、提交父子关系、tree 和文件原文/SHA256；最终提交链接见本轮交付。未上传第三方数据或原始源码。

**给颜老师的一句话：** ArtiPoint 确有作者未解释的边界消融反常，但现有证据还无法区分前端/配对混杂、运动可辨识性与已知滤波效应。是否值得取得一份小型真实缓存做一次因果诊断，可以讨论；把它当成已成立的创新点或立即投入新算法，当前依据不足。
