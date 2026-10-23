> 历史发布副本（2026-10-23归档）。本机路径与第三方原文按需移除；原始/发布哈希和遗漏见归档 PUBLICATION_MANIFEST.json。文中当时的后续建议及授权已经终止，以根目录 EQA_RESEARCH_DECISION.md 为准；未发布附件只在本地保留。

# 离线测试结果

日期：2026-10-23。测试源为 [test_offline.py](tests/test_offline.py) 与 [worker.py](tests/worker.py)，下载器为 [bounded_resume.py](scripts/bounded_resume.py)。

最终结果：**26 项测试方法通过，0 失败、0 错误，耗时 7.332 秒**。包含子场景的测试不按独立测试方法重复计数。

## 覆盖与观察

| 测试组 | 已验证行为 |
| --- | --- |
| 完整传输与逐块日志 | BODY 合计等于完整缺失字节；候选文件与合成原文件逐字节相同；COMMIT 前存在 BODY |
| 正常停止后续传 | 完成当前 16 KiB 测试请求后停机，下一次从已提交偏移续传，接收量不重复或重置 |
| 真实 SIGINT / SIGTERM | 每种信号覆盖 BEGIN 后、HEADERS 后、read 后、BODY 后、文件写后、COMMIT 后；另外覆盖阻塞读，共 14 个子场景 |
| 短响应与断点 | 收到 3,072 bytes 后断开，持久偏移相应推进；整次 16 KiB 预留保留；下一次从正确偏移续传 |
| 超时 | 不伪造完整响应，保留已记录下界和请求预留 |
| 强制退出四个窗口 | read 后未入账、BODY 后未写、写后未提交、提交后未结算；前两类保守恢复，已写未提交尾部拒绝自动恢复 |
| 重复接收计费 | BODY 已记录但未提交的失败请求，后续再收的同一字节计入新增接收量；原预留不退回 |
| 11 类协议错误 | 200 忽略 Range 并返回整份合成文件；范围、total、长度错误；ETag 改变/变弱；gzip；chunked；302；412；类型错误均停止 |
| 预算 | 网络前发现额度不足不请求；磁盘不足在初始化与逐块阶段停止；未决预留导致余额不足时不自动重试 |
| 身份与账本 | 原前缀改变、候选被篡改、最终 MD5 错误、账本截断/改写均拒绝 |
| 同时运行与链接 | 第二个实例被锁拒绝；候选软链接、硬链接和工作目录软链接被拒绝；合成原前缀保持 hash |
| 远端隔离 | offline 非 loopback 地址拒绝；真实官方 URL 在未批准生产配置下联网前拒绝 |

## 测试材料和网络范围

合成数据大小：65,659 bytes；SHA-256：`b19686087df7ac0efa029b4ade616d25fb4aa28ee996b17e2132a065d7158bbf`。内容由确定性公式生成，没有视频或个人资料。

run3 共 97 次 loopback GET；外部请求 0，真实媒体请求 0。测试服务仅绑定数字 `127.0.0.1` 随机端口，结束后已关闭。redirect fixture 指向的测试地址从未跟随。

所有真实 SIGINT/SIGTERM 在子进程内执行，4 类强制退出使用 `os._exit(87)`。没有向用户应用或原下载进程发送信号。链接和篡改测试仅操作 `results/test_runs/` 中的合成测试文件。

## 保留日志

- `results/TEST_RUN_1.log` 与 `results/TEST_SUMMARY.json`：沙箱不允许绑定本机端口，0 项测试，不能计为通过。
- `results/TEST_RUN_2.log`、`results/TEST_SUMMARY_run2.json`：首次有效运行，26 项通过。
- `results/TEST_RUN_3.log`、`results/TEST_SUMMARY_run3.json`：补强整文件 200 回退场景后，最终 26 项通过。
- `results/LOOPBACK_REQUEST_LOG_run3.json`：最终 loopback 请求范围记录。
- `results/test_runs/run3/`：每个合成案例的账本、候选与子进程输出。
- `results/REMOTE_DISABLED_CHECK.json`：对真实生产计划的本地拒绝结果 `REFUSED_BEFORE_RUN / REMOTE_NOT_APPROVED`；未连接远端。

本次结果证明这些本地故障场景的实现行为，不证明真实服务器的 TLS、速度或 MP4 像素/PTS 可用。未测线路总字节或断电恢复；任何未决请求仍按保守上界收费。
