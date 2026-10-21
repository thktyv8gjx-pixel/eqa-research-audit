> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# StreamEQA 精读与输入协议差异

核验日：2026-10-21。[arXiv:2512.04451v1](https://arxiv.org/abs/2512.04451v1)，[CVPR 2026 Findings正式条目](https://openaccess.thecvf.com/content/CVPR2026F/html/Wang_StreamEQA_Towards_Streaming_Video_Understanding_for_Embodied_Scenarios_CVPRF_2026_paper.html)。本地 `papers/stream.pdf` 21页；已读正文p1–8，附录其余题目示例未逐项读。它是具身场景视频问答，**不执行可改变环境的闭环导航/操作**。

**论文原文——方法/数据。** Benchmark基于[HD-EPIC](https://hd-epic.github.io/site/)，不是EPIC-KITCHENS-100的随意替代；156段长视频、20,731 QA、42细类，感知/交互/规划 × 回溯/当前/预测（p2–5）。规划题衡量对动作序列的回答，不等于真实执行策略成功率。原视频官方另有下载入口，未下载。

**论文原文——评测输入与指标。** p6 §4.1把离线Video-LLM改为仅看事件起点te到提问时刻tq；离线评测能看完整视频是单独对照。MCQ Accuracy按类别/时间维度统计。p7表2 Qwen3-VL-8B总51.7、感知63.0、规划42.0；p8表3 EgoGPT离线62.03、在线60.93，差1.10个百分点。这是作者报告；单次表格不能证明推理误差的具体原因。

**作者自述不足。** 无独立通用Limitations章。p7–8承认交互/规划弱于感知、流式限制影响表现，长程时间信息与因果推理仍不足。源数据主要厨房活动（p2、§3），没有真实闭环效用实验。不把我对泛化的疑问冒称作者失败实验。

**失败证据边界。** 细类错误率、在线/离线差及题型例子是现有证据；本轮已读部分没有公开逐例“错误预测+正确证据帧+失败归因”的完整轨迹包，不能据此断言某个错误必定由窗口截断引起。需要下一阶段逐例核对。

**静态源码事实。** [仓库](https://github.com/MrYF-Wang/StreamEQA)，提交 `01dc44aaef2a450ff245e9056fa39ee59bf75d5f`。`streameqa/benchmark/infer_online.py` 默认context_time=64；`streameqa/utils/video.py` 的compute_online_window取[max(0,tq−64),tq]，调用仅用realtime字段，未用事件起点。还会跳过过短/缺视频样本、对边界取整，并在窗口内最多约64帧采样。上述为静态阅读，未调用视频处理或模型。公开标注三文件可见；官方源码行为不能直接宣称复现了论文te窗口。

**我的解释/待证伪。** 先比较输入权限对齐后的历史证据覆盖，再讨论预算下记忆；按需检索、均匀抽帧、最近窗口应为强简单基线。本文§2所列VideoLLM-Online、FlashVStream、Dispider、TimeChatOnline均为直接威胁（出处为上方StreamEQA原文及其参考文献）；本轮未独立精读、核验这些方法的版本，不宣称“该子领域空白”。
