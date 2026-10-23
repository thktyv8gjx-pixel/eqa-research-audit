> 历史发布副本（2026-10-23归档）。本机路径与第三方原文按需移除；原始/发布哈希和遗漏见归档 PUBLICATION_MANIFEST.json。文中当时的后续建议及授权已经终止，以根目录 EQA_RESEARCH_DECISION.md 为准；未发布附件只在本地保留。

# GitHub 接入与资产迁移审计

检查始于2026-10-22，跨日完成于2026-10-23（Asia/Shanghai）；目录保留启动日期。迁移基线：`e8627bc729579268cb6c54cdb00f6a484f3e8ede`。

## 安全接入结果

- 原 Windows 根目录为用户提供的 `D:\创新实践`；本机没有该盘的直接访问，本轮不声称完成原盘备份恢复。
- 当前工作区真实位置 `${HOME}/Research`，初始为空，且不是 Git 仓库。小写 research 与大写 Research 为相同目录。
- 目标子目录初始不存在冲突。本轮正常 clone 到 `${EQA_WORKSPACE}`，没有在父目录 git init。
- 仓库：[thktyv8gjx-pixel/eqa-research-audit](https://github.com/thktyv8gjx-pixel/eqa-research-audit)。origin 的 fetch/push URL 均为 `https://github.com/thktyv8gjx-pixel/eqa-research-audit.git`；存在 push URL 不代表授权 push。
- 分支 `main`，跟踪 `origin/main`；本轮 clone 时二者均指向完整 SHA `e8627bc729579268cb6c54cdb00f6a484f3e8ede`。HEAD 提交时间 2026-10-21T23:46:25+08:00，说明为 “Correct selected trace field count to fourteen”。前一提交 `31a5b13e5cd6d8b0cc26d67c2f4633a51164332a`。
- clone 完成后初始 `git status --porcelain=v1` 为空；30 个跟踪文件。报告新增后只有 `local_migration/` 为新未跟踪目录，未提交。未 pull、reset、clean、checkout 覆盖、移动或删除资料；未 commit、push 或修改 remote。

首次 clone 因沙箱 DNS 失败，随后获准的同一标准 clone 成功。GitHub 连接器也确认仓库可访问。没有用文件下载副本冒充 Git checkout，没有降级到不明镜像。

## 发布清单完整性

实际解析 `RELEASE_MANIFEST.json` 全部 26 项，将每份本机文件的 SHA-256 与 `publication_sha256` 比对：**26/26 相同，0 缺失，0 不匹配**。另 4 个跟踪文件为 README、两个索引清单及 .gitignore，共 30 文件；manifest 没有为所有 30 文件提供 publication hash，不能写 30/30 manifest 校验。

每项 manifest 都标记 `edited_copy=true`，保留 `source_sha256` 与 `publication_sha256` 两套 hash。前者对应 Windows 原件，后者对应去机器路径/改链接/删原始行数值后的发布文件。**恢复发布副本，不等于恢复 source 原件。** 本轮不能对不存在的 Windows 原件重算 source hash。

报告中原有“215/138 份 hash 检查”等数字是历史审查范围，本轮没有找回这些文件，也没有重新完成这些原件检查。此次实际验证范围是 26 份发布成果及当前 30 个跟踪文件的保护快照。

## 已恢复的资产

| 资产 | 本机恢复情况 | 完整性边界 |
| --- | --- | --- |
| 原创审计成果 | 清单内 26 份全部恢复且 hash 匹配 | 是经过发布转换的副本 |
| 研究首页和来源索引 | README、RELEASE_MANIFEST、SOURCE_INDEX、.gitignore 已恢复 | 不提供上游素材额外许可 |
| 阶段一 | 4 份 reports、8 篇笔记及目录、候选/局限表及说明、日志 | 历史推荐已被后续 gate 修订 |
| 阶段二 | 整体 gate、反证、最小协议、字段矩阵及日志 | 是静态审计；没有模型或仿真成绩 |
| PTP 单条链审查 | GATE_DECISION、MISSING_REQUIREMENTS、TRACE_EVIDENCE 和日志 | 完成记录已恢复；原始 JSON/图片包未恢复 |
| Git 历史 | 本轮标准 clone 获得当前公开历史与 refs | 不等于 Windows 原目录的全部 Git 或非 Git 内容 |

CSV 已实际解析：candidates 16 行、limitations 24 行、DATA_FIELD_MATRIX 170 行（均不含表头）。

## 未恢复资产登记与权限

`SOURCE_INDEX.json` 共 **192 条来源记录**：156 条有 URL，36 条写“未核实”；192 个 local_reference 对应文件在本克隆目录中均不存在。它们是历史文件的来源/hash/大小线索，不能称这些文件从来不存在，也不能把 URL 数量当可匿名获取数。逐项恢复登记见 `ASSET_RECOVERY_REGISTER.json`，未下载各项 payload。

索引扩展名统计：13 PDF、6 PNG、12 TXT、30 Python、46 JSON、43 HTML、27 Markdown、9 YAML、3 CSV、2 shell、1 无扩展名文件。这 192 条不是完整 Windows 文件清单；某些只在历史报告提及的审计脚本、派生证据与私人资料可能没有逐项索引。

| 类别 | 发布清单明确的排除范围 / 现状 | 可接受恢复来源 | 权限与处理方式 |
| --- | --- | --- | --- |
| 论文 PDF/全文 | 排除；索引有 13 PDF 记录及全文 TXT 等 | arXiv、CVF、ACL、作者官网等正式来源 | 官方公开可读不自动允许打包再分发；固定论文版本/hash，按需另取，不批量下载 |
| 第三方源码快照 | 排除；索引含源码/README/tree 元数据 | 已记录 GitHub commit/blob；只有 main/HEAD 的条目需核版本 | 遵循各仓库许可；当前 upstream 不能自动替代旧快照，更不能据此重写历史证据 |
| 原始数据/逐行摘录 | 排除；PTP 完整数值及旧 schema 中间件不在发布副本 | 固定官方 JSON；或 Windows/备份中的合法原件 | 本轮只登记；数据许可另核，不把代码 MIT 扩大到所有数据 |
| 论文截屏/图像 | 排除；6 PNG 来源标“未核实” | 原 Windows/备份；或确认父 PDF 版本、页码、渲染参数后重建 | 重建图不能保证原 hash；无来源时保留未恢复，不网上随意补图 |
| PTP 轨迹/派生图片 | 历史审查只取得引用，实际图片数 0；本轮仍未取得 | 官方 Drive 包中的精确小文件；先清单/大小/hash/许可 | 不私下下载整包；HM3D 派生图许可未核。当前不能证明包已下架，也不能证明可读 |
| HM3D / ScanNet / 场景 | 未随仓库发布，历史没有完成完整包下载审查 | 数据集官方申请/授权渠道 | 需要相应条款/申请；用户确认资源与下载范围后再取得；上游代码许可不覆盖场景 |
| HD-EPIC 视频 | 未随仓库发布；D3 候选的外部资源 | [HD-EPIC 官方页面](https://hd-epic.github.io/site/) | 官方页标 CC BY-NC4.0，商业使用需另询；MP4 总量 115.5GB，仅登记，不全量下载。单文件/片段取得方式和大小还需核 |
| 老师材料/隐私资料 | manifest 排除 teacher materials、credentials/machine configuration | 由本人从原盘/备份选择性迁移；老师材料需权利人允许 | 不搜索网盘、不索取凭据、不上传 GitHub；无法仅凭此仓库重建 |
| 无关旧项目 | manifest 排除 old unrelated research | 原盘/备份，单独目录 | 不移入 EQA，不删除、不假定不重要 |
| 模型权重/完整实验日志 | README 明示不含模型；历史无完整复现/训练实验 | 模型官方源（将来）；已有真实日志只能由原件恢复 | 没有发生的实验不能“补恢复”；不得生成伪日志 |

manifest 只给出排除类别，没有为每个文件逐一注明是版权、许可、隐私还是发布体积原因；本报告不擅自替每项做法律归因。

156 个 URL 中有官方网页、API、动态 main/HEAD，也有历史挑战/失效页面线索。**没有逐一做 156 个链接当前可达测试**。因此恢复等级是“有定位线索、需重新验证”，不是“已经恢复”。36 个未核实源以及派生图/文本优先找原件或父资源，不推测下载地址。

## 还不能恢复的研究材料

PTP 完整 run 身份、相机逐帧 pose、实际执行动作/后观察、同状态替代分支及剩余预算，在已经审查的公开记录里没有充分证据；这类缺口不是重新 clone 就能补齐。历史 `annotated_frontier_data.json` 在索引的保存大小与 TRACE_EVIDENCE 所列 Git 树大小还相差 1 byte，原件不在本机，不能在此断言字节级恢复；以后应以固定 blob/下载后 hash 核对，不猜原因。

向导师申请交互资源是 D1 重新准入条件，不是本轮已取得的许可。本轮没有联系他人或提交资源申请。

## 保护和复核

新材料只位于 `local_migration/2026-10-22/`。`AUDIT_EVIDENCE.json` 保留命令、26 项 hash 与 30 个跟踪文件的写入前 SHA-256；交付前再次对比，确保历史文件未变。`.gitignore` 原样保留，不把全局 ignore 改成隐藏资料的方式。恢复登记只记录来源和条件，不宣称找回整个 `D:\创新实践`。
