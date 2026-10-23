> 历史发布副本（2026-10-23归档）。本机路径与第三方原文按需移除；原始/发布哈希和遗漏见归档 PUBLICATION_MANIFEST.json。文中当时的后续建议及授权已经终止，以根目录 EQA_RESEARCH_DECISION.md 为准；未发布附件只在本地保留。

# id4370 授权后资源与传输报告

日期：2026-10-23，Asia/Shanghai。工作区 `${EQA_WORKSPACE}`。本次用户已明确批准一个官方视频、有界 Range 探测及人工证据核验；授权记录见 `AUTHORIZATION.json`。**本轮因传输计数失去精确性而停止，完整原件未获得。**

## 固定身份与来源

- 样本：StreamEQA Interaction id4370，任务 EMM，视频 `P01-20240202-110250`。
- StreamEQA commit：`01dc44aaef2a450ff245e9056fa39ee59bf75d5f`；本地研究仓库基线：`e8627bc729579268cb6c54cdb00f6a484f3e8ede`。
- 原始问题：`[third-party annotation text omitted; StreamEQA Interaction id4370 at pinned source]`
- 原始参考答案：`[third-party annotation text omitted; StreamEQA Interaction id4370 at pinned source]`；`gt=1`。完整原始行复用 `../D3_SINGLE_CASE_2026-10-23_ID4370/FROZEN_CASE.json`，没有改写。
- 提问 288.65 秒；旧候选 187.89–200.78 秒；最近窗口 224.65–288.65 秒。

官方唯一 URL：

`https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/Videos/P01/P01-20240202-110250.mp4`

期望完整大小 **357,839,862 bytes**；期望完整 MD5 **`c981eab775c96858da313acef769b014`**。来源为[官方固定 MD5 清单](https://github.com/hd-epic/hd-epic-downloader/blob/d3431a3a9051cbcadeca98fbb86137605a017525/data/md5.txt)，对应精确 `.mp4` 项。Range 与完整 GET 的响应均指向该 URL，ETag 为 `"664fd8fc-155433f6"`，总大小与下载前一致。

## 许可沿用与用途

复用本日已经保存和核验的[项目页](https://hd-epic.github.io/site/)及[数据内部 readme](https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/readme.txt)：数据内部指定 **CC BY-NC 4.0**，署名 Toby Perrett 等，HD-EPIC: A Highly-Detailed Egocentric Video Dataset (2025)，保留[许可链接](https://creativecommons.org/licenses/by-nc/4.0/)。Bristol 通用记录中的 BY 4.0 字段差异继续保留，不据此扩张用途。

本轮为用户批准的本地非商业科研核验；没有发现新的许可、来源或版本变更，也未宣称既有许可差异得到澄清。未联系作者，未上传媒体。没有重做文献与全量元数据审查。

## 已执行的传输

| 请求 | 结果 | 响应体计量 |
| --- | --- | --- |
| Python 标准库首次连接 | 连接被对端重置，没有取得 HTTP 响应体 | 客户端读取 0 bytes |
| 系统 curl，`Range: bytes=0-65535` | HTTP 206；`Content-Range: bytes 0-65535/357839862`；版本与大小一致 | **精确 65,536 bytes**，curl 最终统计已保存 |
| 系统 curl，完整单文件 GET | HTTP 200，Content-Length 357,839,862；下载较慢，助手为切换续传主动发送 SIGINT | 最终 curl JSON 未产生；**实际响应体接收量无法精确恢复** |
| 中断之后 | 未启动续传或其他媒体请求 | 0 次新增请求 |

完整 GET 设置了 `--retry 0`、不跟随重定向、固定 `If-Match` 和 `--max-filesize 357839862`。中断后脚本解析空的 curl 输出失败，历史 ledger 只保留已完成探测的计数；**不能将其中 65,536 当作本轮总传输量**。权威核对记录为 `logs/TRANSFER_ACCOUNTING_RECONCILIATION.json`。

这是助手在切换续传时的处理失误，不是用户未授权，也不是官方文件 hash 已被证明错误。没有把文件落盘大小当网络实际接收量，也没有用“剩余磁盘够”代替网络预算证明。

## 字节账本与停止依据

| 项目 | 数值与含义 |
| --- | --- |
| 已保存的完整文件前缀 | **17,821,696 bytes**；不是完整视频 |
| 已完成 Range 探测 | **65,536 bytes**，未超 2 MiB 探测上限 |
| 本轮总媒体响应体精确值 | **未知**，不能报告虚假精确数字 |
| 总媒体响应体可证下界 | **17,887,232 bytes**＝已保存前缀＋独立 Range 响应 |
| 总媒体响应体保守上界 | **357,905,398 bytes**＝一个完整 GET 的 Content-Length 上界＋Range 响应 |
| 用户总上限 | **359,937,014 bytes** |
| 按保守上界仍可保证的剩余额度 | **2,031,616 bytes** |
| 补全当前前缀尚需文件字节 | **340,018,166 bytes** |

本轮已发生传输的保守上界仍在授权内，没有证据表明已经超限；但精确计数缺失后，无法证明继续获取全部缺失字节仍满足累计上限。因此依用户“预算异常即停止”的边界终止媒体工作。这里的范围指客户端 HTTP 响应体；TLS/TCP/DNS 线路开销未计量。

## 保留文件及 hash

仅将本轮新生成的不完整下载改名为 `media/P01-20240202-110250.mp4.partial`，防止被后续程序误认成原件；历史文件没有移动或改写。

- 部分文件大小：17,821,696 bytes。
- **部分文件** MD5：`1a8ec3ade3172a78571d5fa4629f2403`。
- **部分文件** SHA-256：`7639ef70768aba2c8af4652056bdf95183636e44b4738e22b2b2bb8c136fc6ee`。
- 64 KiB 探测片段 SHA-256：`804e0c8645010f7674c5fb07f052af6bdd222a60653480d043d84f51780157ad`，与已保存前缀的前 65,536 字节逐字节一致。
- **完整原视频本地 MD5 / SHA-256：未取得**。不能将部分文件 hash 与完整官方 MD5 不同解释为内容损坏或来源异常。

当前新增目录约 18.2 MB，精确终值见 `FINAL_VERIFICATION.json`，低于 512 MiB。原生工具编译产生的缓存仅在本轮目录内创建并清理，清理日志保留；未删除原件、媒体前缀或历史资料。未安装软件、未下载其他资源。所有媒体和临时目录有本地 `.gitignore` 保护，且未执行 commit/push。
