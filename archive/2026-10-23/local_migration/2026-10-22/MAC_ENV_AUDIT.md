> 历史发布副本（2026-10-23归档）。本机路径与第三方原文按需移除；原始/发布哈希和遗漏见归档 PUBLICATION_MANIFEST.json。文中当时的后续建议及授权已经终止，以根目录 EQA_RESEARCH_DECISION.md 为准；未发布附件只在本地保留。

# Mac 科研环境审计

环境检查始于2026-10-22，报告跨日完成于2026-10-23（Asia/Shanghai）。目录沿用启动日期；硬件与工具版本是本轮检查快照。本轮只核查、恢复文献上下文和制定准入计划，没有安装科研依赖、创建虚拟环境或执行研究实验。

## 结论

本机已经具备文献阅读、Git 管理、Python 标准库元数据处理的条件；尚未具备已验证的 PyTorch MPS、视觉语言模型或 Habitat 执行环境。24GB 是 CPU/GPU/系统共享的统一内存，不能计作 24GB 独立显存。

## 工作区和硬件实测

| 项目 | 本轮结果 | 取证方式 |
| --- | --- | --- |
| 初始工作区真实路径 | `${HOME}/Research` | `pwd -P` |
| 大小写别名 | `${HOME}/research` 与上述目录为同一对象 | 两路径设备号 16777233、inode 1187121 相同，`os.path.samefile=True`；不是创建了两个目录 |
| 初始内容 | 空目录，无 `.git`、项目、未提交文件或可见用户资料 | `ls -la`、`git rev-parse`；只描述该工作区，不推断整台电脑没有资料 |
| 当前 EQA 根目录 | `${EQA_WORKSPACE}` | 本轮在无冲突子目录正常 clone |
| 机器 | MacBook Air，Mac17,3，Apple M5 | 只读 `system_profiler` / `sysctl` |
| CPU / GPU | CPU 10 核（4 Super + 6 Efficiency），GPU 10 核，Metal 4 | `system_profiler` |
| 架构 | arm64；当前 Homebrew Python 为原生 arm64 | `uname -m`、`platform.machine()` |
| 内存 | 25,769,803,776 bytes，即 24 GiB；系统显示 24 GB | `sysctl hw.memsize`、硬件概览 |
| macOS | 26.6，build 25G72 | `sw_vers` |
| 数据卷 | 总容量约 926 GiB，可用约 851 GiB | `df -h`，审计时快照；与标称 1TB SSD 口径不同 |
| Command Line Tools | `/Library/Developer/CommandLineTools`；Apple clang 21.0.0；SDK 27.0 | 路径和命令已实际读取；SDK 版本不冒充运行系统版本 |

首次沙箱内硬件/进程读取受限，随后获准的只读查询成功。未发现 brew/uv/pip 安装进程；看到了 macOS 软件更新后台服务，这不证明有正在进行的安装，不停止这些服务。

## 已有工具和未发现的软件

| 工具 | 版本 / 状态 | 可用性口径 |
| --- | --- | --- |
| Git | 2.56.0，`/opt/homebrew/bin/git` | 命令及本仓库 clone/status 成功 |
| Codex CLI | 0.163.0，`/opt/homebrew/bin/codex` | `--version` 成功；沙箱提示不能创建 PATH aliases，不能据此认为 CLI 未安装。桌面宿主版本没有独立核实 |
| uv | 0.13.5，Homebrew aarch64 构建 | 命令可用；未重装 |
| Homebrew | 7.0.10，`/opt/homebrew/bin/brew` | `--version` 和只读已装清单成功；没有 update/upgrade/install |
| 默认 Python | Homebrew CPython 3.15.0；pip 26.2.2 | 执行器 `/opt/homebrew/opt/python@3.15/bin/python3.15` |
| Apple Python | `/usr/bin/python3`，3.9.6 | uv 已装解释器盘点识别；不修改系统 Python |
| Python 3.12 | 检查范围内未发现 | PATH、uv only-installed、常见环境目录均未发现；尚无独立 3.12 环境 |
| Node.js | Homebrew 清单 26.12.1 | 本轮用于安装状态盘点，不作为 EQA 必需依赖 |
| VS Code | 1.143.0 | 应用 plist 与 brew 清单确认；未验证扩展登录状态 |
| Zotero | 10.0.6 | `/Applications/Zotero.app` 的 plist 与 brew 清单确认；没有检查私人文献库、同步或 PDF 内容 |
| PyTorch / torchvision | 默认研究 Python 未发现 torch；实际导入得到 `ModuleNotFoundError` | MPS 状态为 **NOT_TESTED / NO_TORCH_IN_CHECKED_ENV**，不是 is_available=False 的实测结果 |
| MLX / Transformers | 未发现 | 默认 Python 的模块探测，不等于证明所有隐藏/自定义环境均无安装 |
| Jupyter / notebook | 未发现；PATH 无 jupyter | 没有为了审计安装 notebook 服务 |
| NumPy / pandas / Pillow / OpenCV / PyAV | 默认 Python 未发现 | CSV/JSON/hash 处理已用标准库完成，未测图像/视频流水线 |
| Habitat-Sim / Habitat-Lab | 未发现 habitat_sim / habitat | 没有启动仿真或拉取场景 |
| FFmpeg / ffprobe / CMake | PATH 未发现，brew 清单未列出 | `ffmpeg-python` 本身也未安装；Python 包不能代替 ffmpeg 可执行程序 |
| Conda / Mamba | PATH 未发现；常见 miniconda3/miniforge3/anaconda3/.conda 路径不存在 | 不因此安装一套新包管理器 |

检查范围包含当前工作区、默认 Python 搜索路径/包元数据、Homebrew 清单、PATH、uv 已装解释器、常见虚拟环境与模型缓存目录、`/Applications`。未扫描整盘私人文件或未知自定义环境。默认 Python 包元数据只列 pip。常见 Hugging Face / torch 缓存未发现。

## Apple Silicon 兼容性：分开官方支持和本机运行

### Python 3.12

uv 官方提供指定版本管理，适合以后创建独立的原生 arm64 Python 3.12 环境；本轮没有下载解释器。仓库 30 个跟踪文件是审计成果，没有 pyproject、requirements、lock 或环境定义，不能从它推出一套原 Windows 模型环境。未来应先锁定所选上游 commit、依赖和可用 arm64 wheels，再在独立目录建立环境。3D-Mem 历史复现栈要求 Python 3.9，不应为了统一版本强制改为 3.12。[uv 官方说明](https://docs.astral.sh/uv/guides/install-python/)

`uv python list --only-installed` 首次试图创建只读权限之外的默认缓存而失败；改用 `/private/tmp/eqa-audit-uv-cache` 后成功。这是沙箱写入边界，不是 uv 损坏。本轮没有更改持久 PATH、镜像源或包管理器配置。

### PyTorch MPS

官方 MPS 后端提供 Apple GPU 路径；当前读取到 PyTorch 2.14 文档。Apple 安装页面仍使用 2.11.0 示例，不能把页面示例版本当成本机安装或全局最新版。文档支持并不足以证明本机具体模型可运行。[PyTorch MPS 文档](https://docs.pytorch.org/docs/2.14/notes/mps.html)、[Apple 页面](https://developer.apple.com/metal/pytorch/)

本机未安装 torch，因此本轮没有张量分配、矩阵计算、同步、CPU 数值对照或模型 forward 结果。**MPS 未通过实际运行准入，不能写“已支持/可直接复现”。** 将来只在依赖审查后进行小型环境核验：记录版本与 arm64、is_built/is_available、显式 mps 张量操作和同步、CPU 误差对照、峰值内存；先关闭静默 CPU fallback，若需要 fallback 则单独记录。通过算子测试后仍要验证具体视觉模型和 dtype。

### MLX、轻量 VLM 和视觉编码器

MLX 官方要求原生 Python >=3.10、Apple Silicon、macOS >=14；机器满足硬件/系统前提，软件仍未安装和运行验证。[MLX 安装文档](https://ml-explore.github.io/mlx/build/html/install.html)

后续兼容性试验可考虑 Qwen3-VL-2B-Instruct 这类小模型，以及 SigLIP base 这类编码器，但它们只是候选，当前无权重、实测内存或速度。MLX-VLM 有 Mac 路径，也必须锁定版本及视频时间戳/采样实现；转换权重、量化或更换后端会改变复现配置。[Qwen 官方模型卡](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct)、[Google SigLIP 资源](https://huggingface.co/google/siglip-base-patch16-224/tree/main)、[MLX-VLM 项目](https://github.com/Blaizzy/mlx-vlm)

仅权重粗估：2B FP16 约 4GB、8B FP16 约 16GB（参数量×2 bytes）；尚不含视觉部分的具体结构差异、KV cache、临时激活、解码器和系统占用。4-bit 名义压缩还存在量化元数据/未量化部分，不能据此承诺 24GB 足够长视频或完整系统。

### CPU 数据分析与图像/视频

已实际完成 JSON、CSV、SHA-256 和 Git 元数据处理：16 候选、24 局限、170 字段矩阵行，说明当前标准库路径可用。图像/视频处理仅为有条件可行，NumPy/Pillow/OpenCV/FFmpeg 未就绪；没有把播放器 IINA 的安装当作 Python 视频处理已验证。未来应限制解码帧数、分辨率、缓存字节和并发，记录解码/编码/检索/生成成本。

### Habitat-Sim、CUDA、EGL 和 Linux

不能笼统写“Habitat 完全不支持 Mac”。本轮读到官方 main `57ee4941dc4765240f0f91f70b2c97a919bf9038` 的文档、macos-14 构建 workflow 及 Darwin 构建分支；官方确有 macOS 构建路径。但这不等于本机 M5/macOS26.6、某历史版本和整套 EQA 栈已经安装成功。未核到指定版本 osx-arm64 包的实际可用性，也没有运行验证。[官方构建文档](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/BUILD_FROM_SOURCE.md)、[workflow](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/.github/workflows/install_and_test.yml)

官方 README 明确 EGL headless 参数不适用于 macOS；Darwin 包构建选择非 headless、无 CUDA。官方还提示 v0.3.4 之后不再由 Meta 内部团队积极维护。使用新 main 的构建文件不能替历史 0.2.5 的环境背书。[Habitat-Sim README](https://github.com/facebookresearch/habitat-sim)

已重新读取 3D-Mem 固定版本安装说明：Linux/Python3.9、torch2.0.1/cu118、Habitat-Sim0.2.5 headless、linux-64 PyTorch3D cu118，以及外部 API 配置。这些 wheel/CUDA/EGL 路径不能在 arm64 macOS 原样执行；MPS 也不能代替自定义 CUDA 扩展。HFLEX 的 Ubuntu/ROS2/Hydra 等历史约束见候选表，未在本机执行。[3D-Mem 安装来源](https://github.com/UMass-Embodied-AGI/3D-Mem/blob/f445e0828a2c5d5845ccdbd0992fc5eed871d19a/README.md)

StreamEQA 固定版本的 Qwen3VL adapter 把输入放在 CUDA（若可用）或 CPU，未显式处理 MPS；requirements 未锁版本且未直接列出代码导入的 torch，另需系统 FFmpeg。因此 Mac 移植需单独核设备放置、算子和采样一致性，不能只改一个 device 就称官方分数复现。[适配器](https://github.com/MrYF-Wang/StreamEQA/blob/01dc44aaef2a450ff245e9056fa39ee59bf75d5f/streameqa/models/qwen3vl.py)、[依赖文件](https://github.com/MrYF-Wang/StreamEQA/blob/01dc44aaef2a450ff245e9056fa39ee59bf75d5f/requirements.txt)

## 本轮环境变更

仅正常克隆公开审计仓库、新增本迁移目录及临时 uv 盘点缓存。没有安装 Python3.12、torch、MLX、Jupyter、FFmpeg、Habitat；没有系统 Python 改动。机器能力判断保持“标准库审计已实测，模型/仿真路径未准入”。命令结果和文件 hash 见同目录 `AUDIT_EVIDENCE.json`。
