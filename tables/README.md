> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# 表格口径

- [candidates.csv](candidates.csv)：16篇，每行是一篇论文，C编号不表示排名。paper_id可为arXiv ID、OpenReview ID或正式URL；不强行为每篇捏造arXiv号。方向列明确主动/视频/动作/多agent差异。
- [limitations.csv](limitations.csv)：24条，每行是一项原文事实、作者局限/协议或我的推测；page_or_code_location对应实际阅读版本。shared_paper_count为同组不同论文数量，用于定位共同问题，不是统计显著性。

公开性指实现和任务数据渠道可见；完整资产许可、gated门槛、外部云服务和未核实项均保留。没有统一可比排行榜，也没有虚构本轮实测指标。数值只在精读笔记中按原配置引用。

文件为UTF-8带BOM的CSV，方便中文环境读取。生成时通过Artifact Tool block写入及CSV重新导入比较；不需要额外xlsx即可审查。原始来源保存在papers/sources和repos，检索/完整性检查在logs中。
