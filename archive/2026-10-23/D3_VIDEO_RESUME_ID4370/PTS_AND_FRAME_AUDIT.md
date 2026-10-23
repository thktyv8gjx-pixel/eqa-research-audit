> 历史发布副本（2026-10-23归档）。本机路径与第三方原文按需移除；原始/发布哈希和遗漏见归档 PUBLICATION_MANIFEST.json。文中当时的后续建议及授权已经终止，以根目录 EQA_RESEARCH_DECISION.md 为准；未发布附件只在本地保留。

# id4370 解码、PTS 与抽帧审计

2026-10-23。状态：**NOT_EXECUTED — 完整大小和 MD5 门槛未通过；下载超时后已停止。**

## 已执行和未执行

| 项目 | 本轮结果 |
| --- | --- |
| 单视频 HTTP Range 实际响应 | 已验证 74 次 206 和对应范围，73 次正文完整，1 次正文读取超时 |
| 所需时间片段能独立解码 | 未验证。字节 Range 成功不等于可独立解码的视频片段 |
| 完整视频大小 | 未取得；当前 94,875,356 / 357,839,862 字节 |
| 完整视频官方 MD5 | 未验证；不得使用部分文件 MD5 替代 |
| 容器样本表与 edit list 解析 | 未执行 |
| AVFoundation 实际解码 | 未执行 |
| 容器 PTS / 解码 PTS 交叉核对 | 未执行 |
| 标注秒数与实际像素对应 | 无法判断 |
| 抽帧、联系表或视频裁剪 | 0 个；没有查看任何当前视频像素 |
| 288.65 秒之后的像素输入 | 0 个 |

本次本地新文件仅是连续字节前缀；没有根据字节比例、名义帧率或活动区间推断其中包含哪段可解码视觉证据。

## 本机工具检查

ffmpeg / ffprobe 不在本轮检查到的 PATH 中。没有全局安装、下载解码依赖或创建新 Python 环境。

已有 AVFoundation / AppKit 审计程序保留于前阶段目录，本轮读取并核对二进制身份：

- `../D3_VIDEO_VERIFICATION_2026-10-23_ID4370/tmp/av_audit`：154,504 字节；SHA-256 `fb40c5adbcdb93088b790811d4513a21184150cfad8faba66cbacccc28dae714`。
- `../D3_VIDEO_VERIFICATION_2026-10-23_ID4370/tmp/contact_sheet`：102,976 字节；SHA-256 `bc9f2da466ad20a1692030ec72d2b5f1ffb3e1e413137446592ac5cba0ae37d1`。

这些是**已有可尝试的替代工具**，尚未证明能够正确处理这一个完整视频。本轮没有执行它们，也不能宣称它们已完成 PTS 检验。无需因 ffmpeg 缺席就现在安装；是否需要额外工具，应在完整文件通过身份门槛、现有替代方案实际运行后再判断。

## 已准备但未执行的核验路径

新脚本 [audit_verified_video.py](scripts/audit_verified_video.py) 会先要求下载结果 `VERIFIED`，重新检查完整大小和 MD5，并检查已有原生工具 hash，之后才调用工具。本轮完成结果尚未生成时的本地门槛测试已拒绝执行；停止后也必须拒绝 `STOPPED_ERROR` 状态。

[mp4_timing.py](scripts/mp4_timing.py) 是历史容器解析器的新目录副本，只改输出/输入路径及完整文件校验门槛，历史文件未动；溯源见 [PARSER_PROVENANCE.json](PARSER_PROVENANCE.json)。没有在当前残缺视频上试跑解析或“先看一眼”。

未来若获准继续且文件校验成功，应依次：

1. 解析 movie/track timescale、stts/ctts、edit list，重建展示时间，保留原始 ticks、比例及源/目标映射。
2. 用 AVFoundation 读取样本 PTS；与容器解析的有理数时间逐项或完整多重集比较，解释呈现顺序与解码顺序的差异。出现不一致先 HOLD。
3. 仅输出合法前缀 0–288.65 秒的解码帧，记录 reader 状态、首末实际 PTS、非单调时间与被拒绝的越界样本；完整容器元数据检查不构成未来像素输入。
4. 根据实际 PTS 选择抽帧时间，分别检查 187.89–200.78、224.65–288.65、200.78–224.65 及必要的 0–187.89 历史。精确报告 requested time 与 actual PTS。
5. 不用 `秒数 × 名义帧率` 替代 PTS；不将默认 helper 的整数 224–288 秒裁剪冒充本次 224.65–288.65 秒协议；不得使用 318.45 秒活动结束或未来帧补足解释。

已存官方 readme 明确标注基于 MP4；VRS 的映射 CSV 用于 MP4 与 VRS 对照。这解决来源时间基准说明，**尚不等于本文件实际 PTS 与标注已经验证一致**。[本地保存的官方 readme](../D3_ADMISSION_2026-10-23/sources/hd_deposit_readme.txt)。

核验方案见 [VISUAL_REVIEW_PROTOCOL.json](VISUAL_REVIEW_PROTOCOL.json)。计划、已编译工具和门槛检查，均不算已取得的视觉研究证据。
