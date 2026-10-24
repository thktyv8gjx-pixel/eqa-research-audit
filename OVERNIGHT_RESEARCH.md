# OVERNIGHT_RESEARCH

**当前决定：ArtiPoint 是唯一“有条件复现候选”。本轮交付②：已核实的资源缺口、可直接发给作者的请求草稿（未发送）、一页导师讨论问题。** 创新性尚未确认；缺少缓存不构成假设失败。下一步先排除计分集合变化，暂不进入轨迹、可见性、运动范围或平滑的机制比较。

更新：2026-10-25，Asia/Shanghai。仅维护本文件；停止新增候选，不重启 D1/D2/D3、下载器或 RoboSpatial Z 原点提案。此前三轮筛选、淘汰理由和未运行记录完整保存在 [85bd3a 版历史笔记](https://github.com/thktyv8gjx-pixel/eqa-research-audit/blob/85bd3a431757b2d4015dc7b6da7460ff054df0ed/OVERNIGHT_RESEARCH.md)。本次调整的是小规模探索的优先级与准入顺序，不改写历史结果，也不沿用旧版顶端 NO_GO 作为当前决定。

## 1. 需要解释的结果与当前证据边界

母论文：[Articulated Object Estimation in the Wild，CoRL 2025](https://proceedings.mlr.press/v305/werby25a.html)。数字固定引用可读取的 [arXiv:2509.01708v1，S.1.3 / Table S.2](https://arxiv.org/html/2509.01708#A1.SS3)，不混用旧 OpenReview 稿或声称已独立核对最终 PDF 的表格。

| 作者报告的总体角误差（度） | predicted segments | GT segments |
| --- | ---: | ---: |
| Revolute | 17.14 | 20.24 |
| Prismatic | 14.54 | 11.99 |

作者称结果 “not allowing a clear interpretation”。这些是论文汇总值，**不是我们的复现或配对结果**。论文 §5 / S.1.1 使用交互窗口的一维 IoU>0.5 关联预测和 GT；Table S.2 未给逐交互 ID、两条件各自计分集合及失败明细。仅凭上述均值不能确定同一次交互是否变差，也不能确定变化来自平滑。

本轮唯一待回答的问题：**在同一 GT 交互、沿用作者原始匹配与有效性规则时，GT segments 条件的轴误差劣化是否仍存在？** 两条件都获得有效估计的配对差，与覆盖率和失败状态变化，必须分开报告。

## 2. 已核实的公开资源与缺口

官方代码固定为 [`ec88e43e178616697fbc948d0fdda48c0c880702`](https://github.com/robot-learning-freiburg/artipoint/tree/ec88e43e178616697fbc948d0fdda48c0c880702)；本次读取 main ref 与该 SHA 一致。

| 已实际检查的入口 | 能取得什么；不能据此取得什么 |
| --- | --- |
| [该 commit 的完整递归 Git 树](https://api.github.com/repos/robot-learning-freiburg/artipoint/git/trees/ec88e43e178616697fbc948d0fdda48c0c880702?recursive=1) | `truncated=false`，26 个文件，包括源码、配置、README、teaser；没有两设置的运行结果或交互匹配表。 |
| [README](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/README.md) | 提供场景 raw ZIP、metadata ZIP、相机里程计包。`matched_cues.csv` 是 GT 交互窗口，不能替代两条件预测/失败/误差结果；ToDo 的 Evaluation protocol 尚未勾选。未下载这些包。 |
| [官方项目页](https://artipoint.cs.uni-freiburg.de/) | 介绍数据与方法，Code & Dataset 栏仍写 coming soon，没有结果表下载入口。该栏滞后于已发布代码，不能据此说代码/数据不存在。网页与 README 均列 Martin Büchner 的联系邮箱。 |
| [Releases](https://api.github.com/repos/robot-learning-freiburg/artipoint/releases)；[全部 Issues](https://github.com/robot-learning-freiburg/artipoint/issues?q=is%3Aissue)及两条回复 | Releases 返回空列表；Issues #1 是旧函数名修复，#2 是无效深度可视化说明，均未提供所需逐交互结果。 |
| 论文、补充与本地工作区定向检索 | 论文声明会公开 model predictions，但上述入口未找到对应结果文件；本地未找到 ArtiPoint 运行缓存或结果表。原始数据服务器目录本次无法通过网页工具读取，未检查压缩包内部。 |

**缺口结论的范围：在已核实且可读取的官方入口和当前工作区，没有取得可用于这项配对分析的小型结果表；不声称作者未保存结果，也不声称任何公开位置都不存在它。** 无需为核实这一缺口下载完整场景、模型或重跑前端。

源码进一步说明为什么“只要两个成功结果目录”仍不够：

- [`artipoint.py L164–227`](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L164) 只返回有 queries 的 `valid_segments`；无 query 的原始分段被过滤。GT 输入另在 [L523–537](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L523) 仅取 `VERIFIED` 行。这些过滤是否与论文评测一致，需要作者确认。
- [L342–418](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L342) 只将成功估计加入 `segments_results`，同时保存成功分段索引。它说明存在删选路径，**不证明 Table S.2 实际发生了计分集合变化**。
- [L462–484](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L462) 导出 `segment_i/axis_info.json`、`metadata.json` 和可选 `poses.npy`；`segment_i` / `metadata.id` 按成功结果重新编号，不能作为两设置的稳定 GT 交互 ID。
- [L549–588](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L549) 可保存 `segments.json`、`refined_segments.json`；[L804–823](https://github.com/robot-learning-freiburg/artipoint/blob/ec88e43e178616697fbc948d0fdda48c0c880702/artipoint/track/artipoint.py#L804) 保存 `final_successful_segments.json` 及成功结果。它们是作者可能已有的小文件，仍需 GT 对应关系、最终匹配及失败说明才能恢复分母。

本轮取得逐交互结果表 **0**，可用真实配对 **0**，已执行配对分析 **0**。新增/丢失/匹配失败/估计失败的实际数量均为**未知**，不能填成零。

## 3. 可直接发送的作者材料请求（草稿，未发送）

官方联系来源：[项目页 Contact](https://artipoint.cs.uni-freiburg.de/)；可发给 Martin Büchner，`buechner@cs.uni-freiburg.de`。这是公开联系地址，不据此推定唯一通讯作者。本轮没有发送邮件或创建 Issue。

**Subject: Request for per-interaction results behind ArtiPoint Table S.2**

Dear Dr. Büchner and ArtiPoint authors,

Thank you for releasing ArtiPoint and Arti4D. We are planning a small reproduction study of the interaction-segmentation ablation, before running the full frontend. In Table S.2 of arXiv:2509.01708v1, the reported revolute angular error is 17.14° with predicted segments and 20.24° with GT segments, while the prismatic trend is reversed. We would first like to establish whether the difference remains on the same GT interactions, rather than attributing it to any particular processing stage.

Could you share the existing small per-interaction evaluation tables (CSV/JSON or equivalent) for these two settings, ideally covering the full Table S.2 evaluation? We only need:

1. Stable GT interaction identifiers (scene, sequence, object and interaction/annotation row ID), GT joint type and window, and the evaluation split/eligibility list. Please include all eligible GT interactions, even when no prediction was obtained.
2. Each input/predicted segment's identifier and window, with its mapping through any query filtering and successful-result renumbering; the assigned GT ID and IoU, and unassigned or duplicate predictions. Please retain all attempted segments, not only successful estimates.
3. Separate matching and estimation statuses, including no detected segment, no queries/other frontend exclusion, failed or not-attempted estimation, unmatched predictions and invalid/excluded results, with reasons where recorded. If matching is performed only after successful estimation, the pre-estimation segment windows and failure log would help distinguish these cases without changing your original scoring.
4. The per-interaction axis angular error, revolute axis-position error, and predicted joint type for valid estimates; the original metric units/sign convention, treatment of wrong joint types and failures, and the denominator/weighting used for each Table S.2 aggregate. Missing errors can remain missing; we would not impute them as zero.

Could you also confirm which code/config/data version produced these results (the currently available code is commit ec88e43e178616697fbc948d0fdda48c0c880702), the exact IoU>0.5 assignment rule (including one-to-many/duplicate and tie handling), and the frame/time convention used for windows? We would follow your original assignments rather than choose matches by axis error. If the table corresponds to a different manuscript revision, please identify it.

Existing output files and logs are fine: for example, `segments.json`, `refined_segments.json`, `final_successful_segments.json`, and the small `axis_info.json` / `metadata.json` files, together with the GT association/evaluation output. We are not asking you to rerun the full pipeline. If complete tables are unavailable, an existing paired subset with its selection rule would still support a bounded exploratory check, although it could not establish the full-table explanation. A pointer to an already public result archive would also be very helpful.

Only if an error difference persists on common GT interactions would we later ask about a few paired **pre-smoothing** 3D tracks and visibility masks from both settings, query identities, GT/predicted windows and GT axes, with the coordinate/frame mapping and relevant config. This second-stage request would be limited to a small, preselected subset; no full scenes, RGB-D videos or model weights are needed for the initial comparison.

We would use any shared material within the permissions you specify and would not redistribute non-public data without consent. We are investigating the reported result, not assuming a smoothing failure or claiming a new method. Thank you for your time.

Best regards,
Renyaocheng

## 4. 一页导师讨论：先问“同一交互是否变差”

**讨论对象。** 只保留 ArtiPoint 的 GT / predicted segments 消融作为有条件复现入口。作者总体结果出现不同方向变化，值得用一项低成本分析澄清；当前没有真实配对证据，也没有理由把平滑预设为原因。目标是把“评价对象改变”与“同一对象估计改变”分开。

**为什么先看计分集合。** 换分段会改变 query 生成、前端保留的段和后端成功的段，IoU 匹配又可能改变参与误差平均的 GT 交互。两个总体均值可能在比较不同难度的样本。成功目录编号还经过压缩重排，直接按 `segment_0` 配对会产生错误对应。源码只证明这些通路存在，没有证明它们解释了论文结果。

**唯一分析及所需材料。** 先向作者索取两设置已有的小型结果表，不搭建前端。以同一 eligible GT 交互全集为基准，保留 scene/sequence/object/interaction 的稳定键，沿用作者最终关联；重复预测和匹配冲突单列，不按误差挑配对。逐 GT ID 建立两条件状态表：是否有候选段、能否匹配、估计成功/失败/未运行、是否纳入原指标。匹配失败和估计失败是独立维度；若作者只对成功估计做匹配，须保留此前窗口和日志，不能事后把所有缺失都叫估计失败。

**怎样报告才有判别力。** 列出共同匹配 GT 集合、GT 设置新增匹配、GT 设置丢失匹配、两边均未匹配及未匹配预测；另列共同 GT 内的成功→失败、失败→成功、双方失败和前端过滤。错误类型预测及指标排除单列。对双方都有效的同一 GT 交互，逐项给出 Δθ＝GT-setting error−predicted-setting error，以及旋转轴位置误差差值；按 GT 关节类型分层，报告配对数、均值/中位数及变化方向。Prismatic 位置误差记不适用，失败/缺失不赋零。匹配集合与成功集合分别计数，缺失原因交叉展示，不混成可相加的重复类别。先核对原作者统计口径，再讨论配对结果；小子集不外推整表，也不宣称显著性。

**讨论的三个决策分支。** 共同交互差异消失：支持计分构成解释，到此停止平滑因果猜测。差异主要体现在覆盖或失败转移：先解释检出、匹配与估计能力的不同，不能用成功样本均值代替总体性能。共同交互的有效误差差异仍存在：才进入第二道门，用少量预先固定的真实配对轨迹，区分前端点集/可见性、运动范围及平滑等解释；继续存在不等于平滑致因，更不等于创新成立。

**请导师决定的一件事。** 是否值得发送上述小表请求，以一次共同交互比较决定后续机制诊断的投入？若暂时拿不到表，维持有条件复现、等待材料；这不是否定科学假设或小样本探索资格，不增加候选，也不以完整重跑替代缺失材料。

## 5. 本轮执行与归档边界

只读取公开论文、官方页面/源码/Issues及本地现有记录，修改本文件。未执行训练、前端、平滑比较或模拟实验；未安装依赖，未下载场景、媒体、模型或轨迹包，未联系作者。没有新增候选专属临时材料；清理 0 文件、释放 0 字节。现有未跟踪用户文档、旧实验及第三方资产均保留。

原创请求草稿、资源核实和讨论文字仅随本文件归档 GitHub；不上传第三方数据。归档父提交为 `85bd3a431757b2d4015dc7b6da7460ff054df0ed`；交付时核实远端 ref、父提交、tree 与本文件原文字节/SHA256，提交链接随最终回复提供。
