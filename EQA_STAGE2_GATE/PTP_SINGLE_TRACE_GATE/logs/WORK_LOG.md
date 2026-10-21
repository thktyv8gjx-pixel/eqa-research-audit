> 发布副本（2026-10-21）：已移除本机绝对路径；未再分发的论文、源码、数据及审计附件链接指向官方来源或来源索引。原件保留在本地。阶段一推荐应结合后续HOLD及PARTIAL_ONLY审计阅读。

# 本轮工作日志

## 2026-10-21：PTP单条证据链准入

- 阅读上一轮准入、反证和最小协议，定位既有PTP commit、DEEPER_SCHEMA示例question/step、JSON和Git树；阶段一判断不作为正确性前提。
- 固定已记question ID，在其两条已标注step间按8项存在/形状规则选step 2。全JSON轻量解析203题/1632步；不执行上游代码。
- 使用官方GitHub连接器读取固定commit的README、LICENSE、offline-calibration.yaml、logger、query、planner、eval_utils、scene、habitat，共9份文本；保存来源、blob并验证Git blob完全一致。旧calibration/runner/config从本地读取。
- 核对路径拼接、egocentric glob、候选缓存、相机外参计算、记录字典、dynamic commit与实际agent_step的先后次序。记录schema与当前生成路径差异，不认定审查commit就是producer commit。
- web只读访问官方项目页；Drive安全预览由web报告不可访问，Chrome报告ERR_CONNECTION_TIMED_OUT。没有点击下载入口，没有获取归档payload/图像。归档大小、格式、成员清单和独立许可均未核实，不能将访问失败写成资源下架。
- 形成3份门槛报告，判PARTIAL_ONLY；不执行研究实验，不把选例当已证实失败。不再以补图片代替分支/预算证据。
- audit_trace.py复核阶段一215份、阶段二138份既有文件hash未变；新文件均在当前子目录，旧日志亦未改写。

## GitHub发布准备（独立于科研准入）

- 用户明确授权新建GitHub仓库；已确认目标 `thktyv8gjx-pixel/eqa-research-audit` 为公开。采用github-safe-publish技能，仅发布原创报告/笔记/表格/来源索引的脱敏副本，排除老师资料、PDF全文、第三方源码、原始数据及私密配置；不添加未经授权的LICENSE。
- GitHub连接器已读到目标账号，但当前暴露工具无建仓接口。CLI默认受限网络代理连接失败；获准外网只读检查仍连接失败。CLI auth status报告无法验证keyring账号；未读取或打印token，不把网络错误当成凭据确已失效的独立证明。
- 只读检查现有系统代理显示关闭、已配置端口未监听；未更改系统/全局代理、安全设置或登录凭据。浏览器新建页转到登录；用户表示优先用连接器，故不再要求网页授权。发布结果另记 `publication/PUBLISH_STATUS.md`，没有远端SHA核验前不报告上传成功。
