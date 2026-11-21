# 文化生成与分析工具

通过当前项目的关键词、知识与规则模板完成文化场景分析，并提供样本数据界面。

发布单位：NGAI-LLMSafeContent。发布分支：`release/1.0`；更新日期：2026-11-21；自研代码许可：Apache-2.0，第三方保留原许可。

## 功能

- FastAPI规则分析与模板回答
- 浏览器样本查询、添加、删除
- 独立数据服务与课题五iframe集成

## 安装与快速开始

Python环境、Node.js ≥18与npm；当前核心规则模式不需要模型令牌。

从公开仓下载同一发布分支：

```bash
git clone --branch release/1.0 https://github.com/NGAI-LLMSafeContent-OpenSource/Project_3_Cultural_Generation_Tool-release.git
cd Project_3_Cultural_Generation_Tool-release
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell改用 .venv\Scripts\Activate.ps1
```

以下命令均以仓库根目录为起点，注释中的外部条件需先准备：

```bash
python -m pip install -r requirements.txt
npm ci
python backend.py
# 另外两个终端分别运行
npm run data
python -m http.server 6321 --bind 127.0.0.1
```

## 使用与输出

打开 `http://127.0.0.1:6321`。API默认6322，数据服务6323。例如向 `/api/analyze` 发送 `{"text":"蒙古包里的聚会"}`。`examples/db.json` 为虚构样例，数据服务会修改该文件；部署时请准备自己的数据副本。

## 配置与外部依赖

当前代码使用规则而非模型推理，分值不代表真实文化准确性。未被当前backend/index使用的PersonalizedSafety-main扩展不作为现行组件捆绑。

真实凭据只在自己的运行环境或平台Secrets中配置，不提交.env、用户上传、模型权重或运行结果。原仓文件中的内网服务地址经发布负责人确认按原样保留，使用者应在本地配置自己的可达服务。

## 验证与已知问题

完成对应依赖准备后运行：

```bash
python tools/release_check.py
```

检查包含发布文件完整性、原仓文件一致性与声明的最小测试。它不会自动下载模型或申请API，也不代表全部真实业务/准确率验收。保留的原仓错误、未运行项及外部依赖见 [KNOWN_ISSUES.md](KNOWN_ISSUES.md)。

## 发布版本与文件清单

本版本以原开发仓主分支提交 `e17be385f5d984e5c07107bfaa9f9e7d043f1fae` 为源。功能实现与对应原文件保持一致；README、许可说明和发布辅助材料单独登记。当前功能的必要源码、配置、界面与运行资源保留，明确弃用的原型、历史结果和开发缓存不捆绑。

- [逐文件发布清单](RELEASE_FILES.md)
- [原仓文件与Git对象对应关系](SOURCE_ALIGNMENT.json)
- [完整文件SHA-256及权限](RELEASE_MANIFEST.json)，校验表为SHA256SUMS

校验值按Git存储字节生成；若原.gitattributes规定检出换行转换，请用Git对象或发布检查脚本校验，避免将LF/CRLF误认为源码变化。各公开平台release/1.0使用同一个提交，平台生成的运行分支不属于此发布清单。

## 反馈、贡献与许可证

请通过 [公开仓Issues](https://github.com/NGAI-LLMSafeContent-OpenSource/Project_3_Cultural_Generation_Tool-release/issues) 提交复现步骤、环境和日志摘要，勿附真实凭据或用户数据。代码问题由课题维护者在原开发仓处理，发布负责人同步审核后的版本；不要仅修一个平台造成分歧。

自研代码采用[Apache-2.0](LICENSE)。模型、数据集、外部服务和第三方代码遵循各自许可与使用条件，见[第三方说明](THIRD_PARTY_NOTICES.md)。
