> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# 候选筛选与反新颖性补充

核验截止2026-10-21。主表16篇见[CSV](../tables/candidates.csv)。纳入依据：2025–2026正式发表或预印本发布、与EQA直接/邻近相关、看见实际代码及任务数据公开渠道。2024首次上arXiv但2025正式发表的3D-Mem/GraphEQA可按发表年纳入，并保留首发日期。主表中“未核实”的细项不补造。

代码可见只证明公开实现存在；没有执行安装/推理。任务标注公开不替代场景许可；HM3D/ScanNet、HF gated集合和外部服务依赖另列。视频问答、oracle截图问答、机器人动作接口QA均在direction列注明，不能凑成16个可直接相互排名的闭环机器人策略。

## 排除或条件保留（不计入16）

| 论文/来源 | 本轮事实 | 处理 |
|---|---|---|
| [CityEQA，2502.12532](https://arxiv.org/abs/2502.12532)；[代码](https://github.com/BiluYong/CityEQA) | main_C/main_NE、Agent/Data/Evaluation目录可见，README声明1412题；完整城市模拟资产/许可链未核实 | 不是断言未开源；因完整场景及任务适配证据不足，不在主表计数。换城市场景本身非创新 |
| [Embodied VideoAgent，2501.00358](https://arxiv.org/abs/2501.00358)；[代码](https://github.com/Embodied-VideoAgent/embodied-videoagent) | 实际object_memory等源码可见，README说明4090 24GB与数据Drive包；本轮未核验论文特定EQA入口和包内完整字段 | 保留为D2反新颖性近邻，不按本轮已核验完整任务链计入。其首次提交实际为2024-12-31，不能仅凭2501当2025首发 |
| [EQA-RM，2506.10389](https://arxiv.org/abs/2506.10389) | 论文指向UNITES-Lab/EQA-RM，本轮访问404 | 未核实代码可用；不把摘要“will release”当已发布 |
| [3DLLM-Mem，2505.22657](https://arxiv.org/abs/2505.22657) | 核验到的官方仓库快照仅泛化README，未看到实际方法实现 | 不计开源实现，仍是空间长期记忆相关威胁；不能推断永不发布 |
| [EfficientEQA，2410.20263](https://arxiv.org/abs/2410.20263) | 核验到仓库只有README/许可层面，未确证实现 | 不计数；不凭名字认定可复现 |
| [NoisyEQA，2412.10726](https://arxiv.org/abs/2412.10726)；[仓库](https://github.com/gibrantaowu/NoisyEQA) | 本轮仅见简短占位README，2024预印本 | 语言噪声压力测试已有直接前作；代码及2025–2026正式状态未核实，不计数 |
| [GSMem，2603.19137](https://arxiv.org/abs/2603.19137) | 作者项目页/论文存在，未证实完整方法实现发布 | 反新颖性保留；与地图/记忆充分相关，不能因缺代码而当文献不存在 |
| [HIMM，2602.15513](https://arxiv.org/abs/2602.15513) | 2026预印本、v2为3月2日；本轮只核元数据/摘要，未全文精读、未证实代码 | D2立项前必补的直接近邻，不声称其未处理有限容量 |
| [FAST-EQA，2602.15813](https://arxiv.org/abs/2602.15813) | 2026预印本已核元数据，实际代码未核实 | 效率方向相关威胁，不计公开代码候选 |
| [全景视点EM-EQA，2609.33288](https://arxiv.org/abs/2609.33288) | 9月27日新稿；作者arXiv声明ACCV录用，未另核正式录用/实现 | 近期视点选择威胁；不冒称已精读或代码公开 |
| [ASENA，2609.39207](https://arxiv.org/abs/2609.39207) | 9月30日首发、10月12日v2；具身导航相关，代码未核实 | 证明检索延伸至10月可核研究；不把纯导航当EQA直接baseline |
| [TANGO，2412.10402](https://arxiv.org/abs/2412.10402) | 找到CVPR 2025论文，官方方法代码未核实 | 搜索还命中另一个同名ICRA traversability项目；禁止把后者代码接到此论文 |

## 发布审查中的纠正

- PQB README下载处是占位，但[作者项目页](https://milesshelton.github.io/pqb_eqa/)链接[Zenodo DOI](https://doi.org/10.5281/zenodo.16112260)，API确认问题xlsx、截图、环境和动作日志5个文件。故纳入主表；本轮只读元数据，未下载文件。
- [MT-HM3D](https://huggingface.co/datasets/zmling/MT-HM3D)、[BridgeEQA](https://huggingface.co/datasets/hoskerelab/bridge-eqa)、[ActionEQA](https://huggingface.co/datasets/TianweiBao/ActionEQA)有真实HF文件清单。Bridge完整包约14.8GB、MT-HM3D仓库存储约10.4GB来自仓库元数据，**不是本轮下载量**。
- ECBench作者旧链接重定向至[DAMOEC/ECBench](https://huggingface.co/datasets/DAMOEC/ECBench)，元数据 `gated=auto`，不写成匿名免许可视频包。
- Sequential发布的序列文件可见，但原seed/源数据revision缺失，使用canonical文件并冻结hash才是可审查的后续路线。

上表不构成系统综述穷尽名单；未检出代码不等于证明没有代码，未精读的论文不能判定没有解决候选问题。
