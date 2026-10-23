> 历史发布副本（2026-10-23归档）。本机路径与第三方原文按需移除；原始/发布哈希和遗漏见归档 PUBLICATION_MANIFEST.json。文中当时的后续建议及授权已经终止，以根目录 EQA_RESEARCH_DECISION.md 为准；未发布附件只在本地保留。

# D3 前缀、预算及支持证据协议核验

2026-10-23。StreamEQA固定commit：`01dc44aaef2a450ff245e9056fa39ee59bf75d5f`。本轮只解析文本标注/源码和独立元数据，不执行官方推理、FFmpeg或评测脚本。下列数字是字段统计，不是错误率或模型成绩。

## 四种输入权限不能混为同一个复现

| 设定 | 可见范围 | 关键权限/风险 |
| --- | --- | --- |
| 论文online的离线Video-LLM输入 | `Video[te:tq]` | 原文§4.1提供事件起点；事件起点是额外边界信息，不能默认部署系统已知 |
| 当前公开代码默认 | `[max(0,tq−64),tq]` | helper只使用realtime/context_time，不使用标注事件起点 |
| 独立全前缀诊断 | `[0,tq]` | 属诊断变体；必须另设相同输入/总缓存预算，不能当成论文原设置 |
| 整段事件/未来可见 | 可包含tq之后 | 仅供单独离线核验或作者offline对照，不能进入因果部署输入 |

论文事实来源：[StreamEQA v1 §4.1](https://arxiv.org/html/2512.04451v1)。这项论文/代码差异此前已发现；本轮补充的是具体字段、分母及样本准入后果，不重复宣称发现新机制。

## 已读取标注及身份

Perception共6,500条、Interaction共7,996条；各文件内部ID均唯一。跨文件身份使用 `(split,id,video)`，不把不同文件的同一数字ID直接拼接。Planning传输超时未保存，不纳入14,496条分母，不声称已检查全部20,731题。原始字节已匹配上游blob；详见资源报告与FETCH_LOG。

Perception每行都有 `inference_basis`，其中数字和数字字符串需要按明确规则归一化。Interaction中该字段既可能为文本、结构化操作列表，也可能缺失；时间字段还分 `start_timestamp/end_timestamp`、`action_start_time/action_end_time`、`task_start_timestamp/task_end_timestamp`。**不能将任意start字段统一重命名为论文te或最小支持帧区间。**

## 时间字段的实测发现

### Perception

13种task各500条。4种Backward task（ARB/OPB/RRB/SUB）共2,000条，其标注区间末端距提问通常仅几秒；本次统计的最大值分别2.00/1.99/3.00/0.50秒。在全部6,500条中，没有一条basis区间完整落在最近64秒左边界之前；RRB有1条跨该边界。该发现**只说明现有时间标注并不直接给出大量窗外支持候选**，不能证明全部必要证据都在窗口内。

4,490条basis区间终点晚于tq，2,492条起点晚于tq。Forward的目标事件本来就可能位于未来，Realtime也可能用跨越tq的整动作标注。这不自动证明官方推理泄漏，却明确禁止把整个basis或其完整描述送给模型当已观察证据。文本caption、动作/答案字段及未来位置都只能放在评估侧。

### Interaction

在 `start_timestamp/end_timestamp` 这一字段对中，完整位于最近64秒窗口之前的记录共104条：AR8、ASR20、EMM56、NAP20。它们是**时间候选**，并非104个已核实的丢证据错误。部分任务的结构化操作列表缺精确逐项时间，部分区间描述较宽的活动；不能从区间距离直接生成必要性标签。

P01目录范围内有5条这类时间候选。最小视频对应 `(Interaction,4370)`：标注区间187.89–200.78、tq=288.65、默认窗口224.65–288.65。该行没有inference_basis；完整高层活动却可延续至318.45秒。早段可能有支持，但窗口中是否仍有同一动作/物体的等价证据未知。不得仅凭旧区间在窗口外，就标注“64秒截断造成错误”。

`TEMPORAL_FIELD_MATRIX.json`逐task、逐命名字段登记计数。不同字段对可能在同一行并存，因此字段计数不可直接相加当独立样本。`ANNOTATION_TEMPORAL_AUDIT.json`保存Perception的区间距提问统计。

## 取整、采样、缓存与分母

静态来源为 [video.py](https://github.com/MrYF-Wang/StreamEQA/blob/01dc44aaef2a450ff245e9056fa39ee59bf75d5f/streameqa/utils/video.py)、[infer_online.py](https://github.com/MrYF-Wang/StreamEQA/blob/01dc44aaef2a450ff245e9056fa39ee59bf75d5f/streameqa/benchmark/infer_online.py)、[metrics.py](https://github.com/MrYF-Wang/StreamEQA/blob/01dc44aaef2a450ff245e9056fa39ee59bf75d5f/streameqa/metrics.py)。

- 连续窗口先计算，再以整数start和整数duration裁剪；名义裁剪终点为floor(tq)。这不是实际帧PTS检验，不能据此断言边界像素一定被保留或丢失。
- helper按 `int(tq)−int(start)≤1` 跳过短窗口。按该条件静态计算，Perception有6条、Interaction有18条会触发此项；还没叠加缺视频、无效选项等其他跳过原因，不能把这些数当实际运行分母。
- 帧率由整数duration和MAX_FRAMES=64决定。最多约64帧不等于相同视觉token、相同解码成本或相同存储预算。
- 缓存名含视频名、floor(start)、end；不含分辨率、采样规则等全部处理参数，已有文件直接复用。将来诊断必须隔离缓存并记录参数，不修改官方历史缓存。
- evaluator会random.shuffle问题，独立调用每个裁剪；若以后加入持久记忆，不能沿用乱序问题更新状态后声称严格因果流式协议。新wrapper必须按视频/tq记录生命周期，与官方逐题裁剪结果分开。
- metrics只将存在非空预测的题计入total。因此正式复现必须另报预期题数、各跳过原因、运行失败及实际评分分母，不能只保留最终accuracy。尚无本轮预测，不存在已测分数。

## D3 应先建立的证据契约

每题至少记录：固定来源/视频hash与时间域；tq；部署可用前缀；独立评估侧候选支持区间；实际PTS；该区间是否看得清；默认窗口内是否存在等价支持；采样后是否保留支持；语义解释存在分歧时标UNKNOWN。仅有节点跨度、原文caption或标准答案均不能替代像素支持。

支持判定分开“足以回答”和“是否必须用这段”。一段旧帧足以回答，不意味着最近窗口无法回答；这两者未分清前，不得宣称证据遗漏或进行算法归因。评估侧未来观察只能用于核真值，不能替部署策略回答。

总预算分开原始帧/磁盘、解码与传输、外部检索特征、索引与图、长期/当前缓存、回答器视觉token和生成时延。WRWS的固定K、OASIS的root上限、APM的prior-session存储率及SelectStream的N/B/M衡量对象不同。先对齐预算契约，再谈对照。

## 协议门判断

已足够确认协议差异、部分真实时间候选和后续核验入口；尚不足以构成可标注必要支持/预算遗漏的小样本集。原文/代码差异不等于算法贡献，字段统计不等于视觉验证。当前为HOLD。
