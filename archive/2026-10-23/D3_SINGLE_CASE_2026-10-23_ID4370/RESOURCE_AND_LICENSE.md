> 历史发布副本（2026-10-23归档）。本机路径与第三方原文按需移除；原始/发布哈希和遗漏见归档 PUBLICATION_MANIFEST.json。文中当时的后续建议及授权已经终止，以根目录 EQA_RESEARCH_DECISION.md 为准；未发布附件只在本地保留。

# id4370 单视频资源与下载前审批记录

核验日：2026-10-23，Asia/Shanghai。阶段：**PRE_DOWNLOAD；等待用户明确批准**。

工作区 `${EQA_WORKSPACE}`；本地 Git 基线 `e8627bc729579268cb6c54cdb00f6a484f3e8ede`。本轮复用 `../D3_ADMISSION_2026-10-23/` 四份主报告、样本清单和资源记录，校验其 37 份来源文件的既存 SHA-256；没有重做文献查新或全量标注统计。

## 冻结样本

唯一身份为 `(StreamEQA Interaction, id4370, P01-20240202-110250)`，任务 EMM。上游标注 commit `01dc44aaef2a450ff245e9056fa39ee59bf75d5f`。

- 原始问题：`[third-party annotation text omitted; StreamEQA Interaction id4370 at pinned source]`
- 原始参考答案：`[third-party annotation text omitted; StreamEQA Interaction id4370 at pinned source]`
- 原始 `gt=1`，与 `options[1]` 一致；四个选项、全部原始字段保存在 `FROZEN_CASE.json`，没有改写参考答案。
- `realtime=288.65`；`start_timestamp="187.89"`、`end_timestamp="200.78"`。
- 高层活动为 `Continue orange juice`，活动范围 187.89–318.45 秒，`operation_count=3`。原记录没有 `inference_basis` 字段。
- 活动结束时间超过提问时刻。318.45 秒不得成为可部署输入边界，活动标签也不构成像素证据。

标注原始文件 SHA-256：`f3ce6abe46f3bfc91542cad97051a74c433b13539436e500f1384587a4186e9e`；Git blob：`80d0c20b86e1853c7328250972a6a3735952f41e`，本轮本地复核匹配。[固定标注来源](https://github.com/MrYF-Wang/StreamEQA/blob/01dc44aaef2a450ff245e9056fa39ee59bf75d5f/data/annotations/Interaction.json)

## 唯一允许申请获取的资源

官方精确 URL：

`https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/Videos/P01/P01-20240202-110250.mp4`

| 项目 | 已核事实 |
| --- | --- |
| Content-Length | **357,839,862 bytes = 341.262686 MiB = 357.839862 MB** |
| 官方期望 MD5 | **`c981eab775c96858da313acef769b014`** |
| MD5 来源 | HD-EPIC 官方下载器固定 commit `d3431a3a9051cbcadeca98fbb86137605a017525` 的 `data/md5.txt` |
| 精确对应项 | `./Videos/P01/P01-20240202-110250.mp4`；没有误用同名前缀的 VRS、映射 CSV 或日志 hash |
| 官方时长记录 | 396.266667 秒，仅是元数据，尚未本地解码确认 |
| 本轮实时请求 | HEAD，HTTP 200，2026-10-23 05:32:04 GMT；无重定向 |
| 响应类型 | `video/mp4` |
| Last-Modified / ETag | `Fri, 24 May 2024 00:02:04 GMT` / `"664fd8fc-155433f6"` |
| Accept-Ranges | `bytes`，仅为声明 |
| 本地原视频 hash | **不存在：尚未下载，未计算本地 MD5 / SHA-256** |

[固定 MD5 清单](https://github.com/hd-epic/hd-epic-downloader/blob/d3431a3a9051cbcadeca98fbb86137605a017525/data/md5.txt)。保存的清单 SHA-256 为 `a2b0f5945114f4af28c87df9d51fab58a71cde33650b4616b5acc5846103d824`。MD5 用于与官方字节清单比对；成功获取后还应计算 SHA-256 作为本地身份记录。

## 许可与来源

沿用本日已保存的官方许可原文：[HD-EPIC 项目](https://hd-epic.github.io/site/)与[数据内部 readme](https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/readme.txt)均指向 **CC BY-NC 4.0**，要求适当署名、链接许可、说明修改，限制商业用途。数据集署名为 Toby Perrett 等，HD-EPIC: A Highly-Detailed Egocentric Video Dataset (2025)。[许可链接](https://creativecommons.org/licenses/by-nc/4.0/)

[Bristol 数据记录](https://data.bris.ac.uk/data/dataset/3cqb5b81wk2dc2379fx1mrxh47)的通用 Licence 字段另列 CC BY 4.0；既有冲突仍未由权利人澄清。本次拟用途限定为本地、非商业科研核验，按数据内部更具体的 NC 条件保留来源和派生说明；不由较宽松字段推导额外再发布权限。

下载批准是用户对本次资源消耗的授权，不是更改第三方许可。未来抽帧仅作本地派生审计材料，记录“从原 MP4 抽帧，必要时缩放并加时间标签”；原 MP4 字节不变。不联系作者，不提交或推送第三方媒体。StreamEQA 的标注与 HD-EPIC 的视频来源分别保留，视频许可不自动替代标注许可。

## 本机状态与预算

本轮检查 PATH、`/opt/homebrew/bin`、`/usr/local/bin`、`/opt/homebrew/opt`、`/opt/homebrew/Cellar`：未找到 ffmpeg/ffprobe。没有据此宣称整台磁盘所有应用内部都不存在解码库。系统 `xcrun swift --version` 实测 Apple Swift 6.4、arm64；尚未用 AVFoundation 解码此文件。未安装软件或创建 Python 环境。

本次环境快照可用空间 **908,197,298,176 bytes，约 845.82 GiB**，位置为工作区所在卷；空间会随系统活动变化。未发现工作区已有该视频同名文件。

审批建议范围如下，**尚未获批或执行**：

| 项目 | 预算 |
| --- | ---: |
| 完整单文件响应体 | 357,839,862 bytes |
| 同一 URL 的有限 Range 验证响应体，合计上限 | 2,097,152 bytes（2 MiB） |
| 视频响应体总读取上限，包含探测及失败读取 | **359,937,014 bytes（343.262686 MiB）** |
| 所有本地新增材料总上限 | **536,870,912 bytes（512 MiB）** |
| 其中抽帧、查看材料等派生文件上限 | 134,217,728 bytes（128 MiB） |

这些是可执行的上限，不是假定已经发生的用量。完整文件占一份空间；新的临时下载文件验证后成为唯一原件，不复制第二份完整视频。不预先生成全视频逐帧图像。失败重试也计入累计预算，不能自动重新下载整文件；预算不够则停止。HTTP/TLS/TCP/DNS 开销不包含在媒体响应体预算中，不能从 HEAD 精确预测线路总字节或下载耗时；实际带宽尚未测速。

## Range 结论和审批边界

**独立可解码片段：UNVERIFIED。** 本轮媒体 GET / Range 请求数均为 0。依据用户原话“在用户明确批准此次单文件下载之前停止，不自动下载”，审批前不读取 MP4 头尾或任何片段。实际 Range 与解码检查也会传输视频字节，因此留待这次明确授权后执行；不能为填写任务一而假报通过。

授权后，最多在上述 2 MiB 预算内检验 HTTP 206、精确 `Content-Range`、总大小与资源版本；收到 200 或不一致区间时不得把整文件响应当小片段保存。还须解析 MP4 初始化信息、样本表及关键帧依赖，并真正用本地解码器验证目标片段。206 成功与“所需时段能独立解码”是两项不同结果。若预算内无法完成，记录“有界探测未确认”，不扩大 Range；完整原件的唯一 URL 和字节预算仍以本表为准。

本轮实际传输：媒体/HTTP 响应体 **0 bytes**；成功 HEAD 的响应头由 curl 记录为 **372 bytes**；首个沙箱 DNS 失败请求没有 HTTP 响应。TLS/TCP/DNS 全线路字节未计量，因此不能说本轮总网络流量为 0。详见 `RESOURCE_PREFLIGHT.json` 与 HEAD 请求记录。
