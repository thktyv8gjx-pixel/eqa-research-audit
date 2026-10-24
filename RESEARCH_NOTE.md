# 具身空间关系：从 RoboSpatial 的公开组件开始

2026-10-25。**只保留 RoboSpatial 一条活跃组件研究线。已运行 12 次原函数＋6 次配对诊断，1 个官方场景；VLM 调用为 0。** 不重跑 ERQA 开发题，不重试 MLX/模型获取。旧提案退出不等于本方法不值得学习。

## 两篇母论文与取舍

**主方法：[RoboSpatial，v5](https://arxiv.org/html/2411.16537v5)。** 输入是图像、相机标定和带方向的 3D 框，输出空间关系/可用位置等标注。先复现 §3.2.1 与 Appendix B.4 披露的空间配置规则：投影决定相机左右，世界高度决定上下。研究理由是这些规则生成训练/评估标签；坐标前提不一致会混淆模型错误和标签错误，而不只是改变一个分数。其原训练收益需要不同 VLM/微调权重，不能由换成 Qwen 2B 代替。局限线索来自公开实现将负世界 z 截为 0；这是源码中的输入假设，不是作者已报告的普遍失效。

**近邻/备用：[CROSS，2026-10-01](https://arxiv.org/html/2610.01999v1)。** 以预测/GT 空间上下文区分感知、表征和推理错误，报告 ReVSI 55.9→60.2，且接入 SpatialClaw。Appendix E 明确说 oracle 干预不等于因果机制独立，算子也预计算了部分答案。此次未核实可直接运行的官方代码入口，因此不进入实现，也不把阅读附录写成其结果复现。

直接比较还保留 [SpatialClaw §F.1/H.1](https://arxiv.org/html/2606.13673v1)（坐标约定、交叉核验已覆盖）与 [RoboSpatialBrain §2.2](https://arxiv.org/html/2606.31645v1)（问句参照系重定向）。这些工作不能直接证明本次公开标注组件的 z 原点问题已解决；反过来，本次组件现象也不能推翻它们的模型结果。没有新增泛搜或预认创新。

## 真正运行了什么

源码固定 [NVlabs/RoboSpatial@7a1b901](https://github.com/NVlabs/RoboSpatial/tree/7a1b901cd86ad980ff6d14c0c1fc9d556ccabb19)。[官方示例图](https://raw.githubusercontent.com/NVlabs/RoboSpatial/7a1b901cd86ad980ff6d14c0c1fc9d556ccabb19/example_data/images/example_dataset/example_scene/example_image.jpg)和相应 `example_input.json` 均取得；图像 162,745 字节，匹配官方 Git blob。它是作者的示例输入，不是独立测试集；3D 标注语义未全面独立裁决。

入口对应：`annotation_generator.py → relationships.get_spatial_configuration → configuration.check_spatial_configuration_relationships`，并调用 `get_object_metrics`、投影占用和可见深度函数。本次直接执行最后这些原函数，**函数体未改写**。缺少 Open3D，因此仅用 NumPy OBB 容器适配其中心/旋转/角点接口；角点顺序和 ZXY 旋转顺序对照 [Open3D v0.19.0 源码](https://github.com/isl-org/Open3D/tree/v0.19.0/cpp/open3d/geometry)。通过 AST 只载入所需函数，跳过模块级 Open3D 导入及不使用的功能。这是明确的组件后端适配，不是完整官方管线原生复现。

只读复用已存在的 Python/NumPy/SciPy/Matplotlib 环境，没有安装包或修改其他项目。版本、来源/输入 hash、冻结条件、完整关系输出保存在 [本轮结果](runs/20261025_robospatial_configuration/config.json)。作者源码、原图、原始场景文件仅在被忽略的 `local_runtime/robospatial_component/`，按 NVIDIA research/evaluation 非商业条款本地使用，不随结果重新发布。

**复现层级必须区分：** 作者披露的关系抽取规则已在其官方示例上实际执行，并复现了相机左右的局部行为；示例没有附作者 golden 输出，本次用图像与几何规则交叉核对。没有复现论文任何性能表、训练收益或独立问答准确率，不能把 18 次函数调用写成 18 道模型题。

## 看懂一个真实样本与关键步骤

原图中间的土豆（对象 0）位于右上香蕉（对象 1）的左侧。关键一步是先以 `T_camera_to_world` 的逆矩阵将框角点转到相机坐标，再用相机内参投影到像素；原代码由投影占用区域判断左右。两种判定模式及三个共同坐标平移条件下，均输出 `camera_centric.left=True`。这说明执行链能产生可解释的正确局部行为，不代表 VLM 从像素恢复了 3D。

值得追的差异是时钟（对象 4）与土豆（对象 0）。原始框中，时钟中心 z 为 −0.65635 m，土豆最高点为 −0.67324 m；按作者 `lenient` 规则的中心/边界定义，其高度判据余量为 **0.01689 m**。这是给定框的计算参照，不是人工重新裁决的物理标签。

将所有框和相机一起平移，物理布局、相机投影和图像都不变。所有角点投影的最大差异为 **3.41×10⁻¹³ 像素**。完整成功、失败及 strict 模式结果都保留：

| 时钟相对土豆的 `world_centric.above` | 原坐标 | 共同 X+1 m 对照 | 共同 Z+1 m |
| --- | --- | --- | --- |
| 原函数，lenient | False | False | True |
| 原函数，strict | False | False | False |
| 仅取消负 z 截断，lenient | True | True | True |

strict 的两个框高度范围相交，不应拿 strict/lenient 差异冒充错误。诊断是在看到首轮结果后提出并执行的；只在内存中移除负 z 截断循环，未改私有原始源码，未增加输入信息。它解释了本组件的翻转，**不是可部署的新方法或论文创新证据**。

## 当前判断与唯一下一行动

- H1：负 z 截断使该组件依赖世界原点。配对消融支持它解释本次函数输出变化。
- H0a：NumPy 适配/投影错误。原生 Open3D 后端尚未对照；极小投影差、X 平移对照及只改截断的结果限制了此解释，但不等于完成原生验证。
- H0b：作者要求地面 z=0，官方示例需预处理；此时问题在输入约定/适配，而不是新的空间推理机制。已读 loader 与调用链未看到对应平移，尚未端到端运行，不能扩大为训练集或模型错误结论。

**CONTINUE_PILOT，仅限核实 RoboSpatial 的输入约定；不提出新算法。唯一下一行动：对同一官方示例核对原生 loader/Open3D 链的地面对齐与输出，区分组件实现问题与输入前提。** 若统一预处理即可解释，就关闭“新推理机制”主张，保留这次组件学习结果。原生 Open3D 未安装；当前只能声明 NumPy 适配组件结果，不为此启动第二个大环境。

完整 VLM 作者结果的共同资源问题一次记录：已有 MLX/Qwen 2B 授权，但先前安装与固定 revision 获取失败，本次未重试；它也不能代替母论文原底模/微调权重。合法解阻需在可达官方来源的既有授权环境取得相符版本/离线包并导入，或作者提供相应合法缓存输出。未取得前，完整模型结果复现仍是 `BLOCKED_RESOURCES`；不换基准、不申请付费服务。

复查命令：用具备 `config.json` 所列版本的现有 Python，设置 `EQA_PYTHON`；执行本目录 `runs/20261025_robospatial_configuration/reproduce_component.py --source-dir local_runtime/robospatial_component --output-dir <新的输出目录>`，再执行同目录 `diagnose_z_clamp.py --source-dir local_runtime/robospatial_component --output <新的诊断文件>`。设置可写的 `MPLCONFIGDIR` 和 `PYTHONDONTWRITEBYTECODE=1` 即可，不需安装 Skill。
