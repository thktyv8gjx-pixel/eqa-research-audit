> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# EXPRESS-Bench / Fine-EQA 精读

核验日：2026-10-21。[Beyond the Destination，arXiv:2503.11117v3](https://arxiv.org/abs/2503.11117v3)，ICCV 2025。`papers/express.pdf` 18页；已读p1–8及p14–15相关分析，其他附录提示词未全部精读。

**原文——研究问题/机制。** 回答正确未必到过支撑答案的位置。EXPRESS同时评估回答与探索；Fine-EQA使用语义/功能区域地图分配探索预算并引导目标搜寻（p3–6）。这已覆盖“加强探索感知评价”和“按区域分配预算”的宽泛想法。

**数据与假设。** p4 §3.2：HM3D/Habitat，777轨迹、2,044 QA；初始/目标位置同层，最短路径10–100步，问题参考终点图像构建，筛除模糊/不可达问题。这是任务范围说明，不是动态场景或任意多层场景结论。

**指标与实验支持。** p4–5 §3.4：语义评分σ，依据最终图像计算的grounding权重δ∈{0,0.5,1}，组合成C；另有C*、E_path及最终到目标距离d_T。p7表2 Fine-EQA C=40.55、C*=63.95、E_path=16.22、d_T=6.43。盲GPT配置C*=58.96说明语义得分可能掩盖证据问题，不能说其C也有58.96。

**作者自述局限/不足。** 无独立通用Limitations节。p4明确单层及终点证据的数据边界；p15 §8.4讨论存在性问题表现偏弱；p8人类与模型差距仍大。将“只看最终图像不适用于历史多视角回答”作为跨任务协议疑问是**我的解释**，不能冒称作者承认评测错误。

**失败案例。** p8图6：都输出浴袍/墙相关答案，只有正确探索位置符合问题指代和证据；p14–15还有可视化与题类分析。这支持分开检查答案、位置和可见证据。已查看p4版面渲染 `papers/figures/express_p4.png`。

**代码/数据。** [官方仓库](https://github.com/HCPLab-SYSU/EXPRESS-Bench)，提交 `e8789dadfbd51af6850dc4d2b0526ca0ee78386a`，入口 `main.py`、原始评价 `evaluation.py`、标注 `data/express-bench.json` 均见静态树。完整HM3D资产另需原许可；本轮未执行或修改评价。

**我的解释/邻近威胁。** 新压力测试应保留原官方分数，另报告历史证据可用性，而不是悄悄改变δ或目标位置。[PQB-EQA](https://aclanthology.org/2025.acl-short.11/)已控制语言先验，[AbstainEQA](https://arxiv.org/abs/2512.04597)已有证据与拒答标签，[Pred-EQA](https://github.com/yuanrr/Pred-EQA)和[Prune-Then-Plan](https://arxiv.org/abs/2511.19768)已针对该benchmark改进规划；“增加难度”本身不够。
