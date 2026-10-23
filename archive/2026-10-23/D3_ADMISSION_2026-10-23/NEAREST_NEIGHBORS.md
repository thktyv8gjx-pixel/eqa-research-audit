> 历史发布副本（2026-10-23归档）。本机路径与第三方原文按需移除；原始/发布哈希和遗漏见归档 PUBLICATION_MANIFEST.json。文中当时的后续建议及授权已经终止，以根目录 EQA_RESEARCH_DECISION.md 为准；未发布附件只在本地保留。

# D3 直接近邻补读

核验日：2026-10-23。阅读范围为原始论文中影响 D3 去留的方法、预算、评测、证据定位与局限部分，以及下列固定版本源码；没有逐项重读所有参考文献或执行代码。所有性能数字均属作者报告，本轮没有复算。

## SelectStream：固定容量与证据定位已被直接研究

原文：[2606.16353v2](https://arxiv.org/html/2606.16353v2)，§3、§4.4–4.5、附录 C–F/H。输入为因果视频流；N 控制记忆节点，B 控制检索子图，M 控制注入证据。骨干冻结，但分段编码、写入门、查询、图推理及校准模块仍需训练；冻结骨干不等于 training-free。论文还报告时间证据 Recall@M/T-Overlap，因此“固定容量+按题保留早期证据+时间定位”不是新的组合。

附录 E 的指标依据节点时间跨度与证据区间的相交/覆盖，不是像素语义必要性证书。该区别是本轮审计解释，不能直接当新颖性。附录 C 段落/公开配置的学习率为2e-4，而表6列2e-5，复现时需要版本澄清。

实现已实际核到：[commit ea10420c1c24d322bb1717a179df66c5e05895ba](https://github.com/Haonan-Ge/selectstream/tree/ea10420c1c24d322bb1717a179df66c5e05895ba)。本轮读 `lvm_memory.py` 的容量及合并路径、Qwen3-VL配置、README；默认 N/B/M=256/64/8。合并保留 min-start/max-end 与加权 latent，所以时间跨度命中不能单独证明细节保存。[合并实现](https://github.com/Haonan-Ge/selectstream/blob/ea10420c1c24d322bb1717a179df66c5e05895ba/main/model/lvm_memory.py#L650-L671)

固定树有56个文件，含实现/配置；没有核到训练后的模块权重，GitHub releases 返回空列表，README使用本地训练产物路径。不能把随机初始化模块当论文系统复现。该树未见独立 LICENSE 文件；当前仅阅读，不据公开访问推断已取得复制、修改或再发布许可。也没有验证 Mac 兼容性。

## WRWS：最近/历史分配及两类失败已有明确对照

原文：[2609.37345v1](https://arxiv.org/html/2609.37345v1)，§0.3–0.6、附录.10/.13–.16。SigLIP 检索已观察历史，以相似度分布的不确定性调节语义与最近性；仅选中观察进入目标模型。约束的是目标视觉处理预算，检索缓存仍随历史增长。附录明确给出“选到相关证据但认错”和“早期证据未选中”的失败区别。

其流式设置按模型族取不同 K（16/4/6），目标约3K视觉token；不是统一帧数，也不是整个系统固定总存储。缓存迁至CPU不消除总存储增长。不能只比较回答器输入、忽略外部编码/缓存/源帧访问成本。论文仍写代码待发布，本轮没有定位并核实一个官方可运行实现；不据此否定已存在的论文贡献，也不声称全球没有代码。

D3若只提出“判断何时检索旧帧”“无训练分配有限帧”或区分上述两类错误，已与直接近邻重叠。

## OASIS：根集合有界与总历史有界必须分开

原文：[2604.17052v1](https://arxiv.org/html/2604.17052v1)，§3、§4.1–4.2、效率及补充案例。training-free 的短窗口/中期缓存/事件森林，先做粗推理，缺信息时产生检索意图并精查；保存QA历史。事件时间段、关键帧、摘要和父子层级都已存在，不能把“可回查事件帧”当空白。

实现：[commit dbd342c79a1b9b03327d4ec5daa87488737db988](https://github.com/Solus-sano/OASIS/tree/dbd342c79a1b9b03327d4ec5daa87488737db988)。读了README、`forest.py`、`types.py`。合并时添加父节点并更新 roots，旧子节点仍留在 `self.nodes`；QA另行追加，检索遍历全部nodes。**根集合上限不是全树或全部QA历史的硬上限。** 这是指定源码路径的静态事实，没有实测内存曲线。[预算维护](https://github.com/Solus-sano/OASIS/blob/dbd342c79a1b9b03327d4ec5daa87488737db988/src/oasis/event/forest.py#L181-L218)

README给出Python3.12/CUDA12.1及Linux x86_64 FlashAttention安装路径，不是本机MPS执行证据。代码许可与视频许可须分开。

## APM-Bench：证据不足识别也已有专门协议

原文：[2609.37559v2](https://arxiv.org/html/2609.37559v2)，§3.1–3.3、§4.1，附录B.4/B.7、D/E相关部分。跨session持久记忆配合当前session因果前缀；Evidence Availability-Aware子集限制可访问历史，并区分证据可得与不可得。存储成本计已完成session的持久状态，排除当前session，不是全链内存的统一上限。该设置与单视频严格容量实验不同，不能混算。

发布状态已核：[代码仓库70ea35f6f414e5692bb569a227ebb77fb9cb637c](https://github.com/Jianguo-Huang11/APM-Bench/tree/70ea35f6f414e5692bb569a227ebb77fb9cb637c)仅README和teaser两个文件；README仍列待发布计划。[HF仓库](https://huggingface.co/datasets/Jianguo-Huang11/APM-Bench/tree/b847a4a8d75ebe9b18bba09000225d747bb34dc4)已有549个MP4，以及README、teaser、.gitattributes，共552文件；在该版本完整siblings清单未见JSON/CSV/Parquet问题标注。不是“空仓库”，也还不是本轮已能逐题联结的替代准入包。只读元数据，未取视频。

## 对 D3 的影响

宽泛方法主张已被覆盖：固定容量、选择写入/合并/检索、按需历史取证、时间定位、证据不足识别，不能通过换数据集重新申请创新。

仍可审查的窄问题是：特定StreamEQA问题的必要支持是否在因果前缀内、却因某明确预算被丢失，以及已有时间指标能否可靠对应语义支持。**当前既无像素证明，也未证明这一严格问题在近邻中尚未解决。** 因此补读支持阻止方法放行，而不是给新方法背书。
