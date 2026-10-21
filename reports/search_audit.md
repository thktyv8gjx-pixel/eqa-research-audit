> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# 检索与证据审计说明

日期2026-10-21；范围为EQA阶段一。研究实验状态 **NOT_RUN**。

## 搜索策略

先检索2025–2026 embodied question answering / EQA及公开代码/benchmark，再沿记忆、探索证据、拒答、跨问题、流式输入和相关动作/多agent任务扩展。来源优先arXiv原文、CVF/ACL正式论文、作者项目/仓库、HF/Zenodo元数据、OpenReview公共记录。除初检已有文件外未读取旧恢复项目作为本轮论据。

完整查询参数和返回结果保存在[logs/sources/](../SOURCE_INDEX.json)。S系列为主题/查新检索，R系列为论文/仓库/评审/发布跟进；编号不连续表示某次工具未完成/未保留，不补造记录。日志原样保留工具返回内容，不能将检索摘要代替原文精读。

主要查询簇包含：2025/2026 EQA github dataset；MemoryEQA / GraphEQA / 3D-Mem / EXPRESS / AbstainEQA / Sequential-EQA / StreamEQA原文；EQA memory 2026；HFLEX/GSMem/HIMM/FAST/ASENA近期元数据；PQB公开数据DOI；OpenReview论文标题/唯一名称及forum归属核对。每次有界读取的URL、字节数、SHA256、时间与错误见 `logs/fetch_*.json` 及请求清单 `logs/scripts/requests_*.json`。

## 执行边界及异常

初始沙箱网络读取报连接拒绝，停止该批并通过标准审批通道重试公开小文件；没有修改网络策略或调用付费服务。GitHub部分API限流403改为普通公开页面/README，无法锁commit处明确记快照而非完整克隆。论文PDF均远小于5GB；未下载任何模型或大型数据包。

OpenReview若HTTP200却为HTML验证页，标记CHALLENGE_OR_NON_JSON，不能解析为评审。搜索API的JSON中有大量仅提及论文名称的其他投稿，按forum/邀请类型归属；文件名不能决定归属。已读评审与未得到全文的区别见[评审报告](public_reviews.md)。

部分arXiv PDF获取缓慢/限额不适合工具，转为CVF正式PDF或作者终稿；每篇笔记明确实际版本、物理页码、阅读范围。AbstainEQA采用正式10页正文+9页补充，补充内容比arXiv HTML更多。图像证据由Poppler渲染检查，见 `papers/figures/`；没有对图表做模型实验。

表格通过Artifact Tool写入、回读CSV对照，并对两表样例渲染检查。CSV中的论文ID是文本；“未核实”不等于0。候选表不含可比性不成立的统一排行榜。

## 验收与未覆盖

验收：16条候选、8篇正文/相关附录笔记、24条局限/协议证据、3个条件方向及公开评审摘要；每行有论文URL/ID，所有主张有类型标记。程序核验只检查文件完整性、CSV结构/链接字段和来源清单，不验证研究假设，也不运行baseline。

未覆盖：所有会议全年穷尽检索、所有候选全文、全部开放审稿、HIMM/GSMem和通用流式方法的完整机制、所有数据包内部内容/所有依赖安装可运行性。因此不对新颖性、最低显存或复现成功作保证。有关缺口已进入主报告去留门槛。
