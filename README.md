# 文化生成与分析规则演示工具

发布方 NGAI-LLMSafeContent；版本 1.0；日期 2026-11-04；Apache-2.0。
源仓库 NGAI-LLMSafeContent/Project_3_Cultural_Generation_Tool，固定提交 e17be385f5d984e5c07107bfaa9f9e7d043f1fae。

此版本公开现有 FastAPI 规则/模板分析器和 HTML 演示界面。源码按关键词识别并拼装回答与演示分值，没有大模型推理；分值不代表文化准确性实测。未包含未确认许可的 PersonalizedSafety-main 训练扩展，也不包含原始数据和模型。

## 前置条件与启动

Python >=3.12、Node.js >=18 与 npm。建议新建 Python venv，再运行：

```sh
python -m pip install -r requirements.txt
npm ci --ignore-scripts --no-audit
python backend.py
```

在另外两个终端分别运行：

```sh
npm run data
python -m http.server 6321 --bind 127.0.0.1
```

访问 http://127.0.0.1:6321 。API 为 6322 端口，数据服务为 6323 端口。APP_HOST/APP_PORT 可配置分析 API；前端 window.PROJECT3_DATA_API_BASE / PROJECT3_ANALYZE_API_BASE 可覆盖地址。页面字体、样式及图表依赖公开 CDN 的联网访问；断网可能影响界面展示。无需配置模型 token。

## 测试与数据

`python tools/release_smoke.py` 自动创建隔离 venv 安装固定 Python 依赖、根据锁文件安装 Node 依赖，然后实际启动分析 API、数据服务和静态页面 HTTP 服务；验证健康、非空/空输入、数据读取与新增删除。使用者需能访问 PyPI/npm。

examples/db.json 仅有 3 条新编写的虚构样例，按 Apache-2.0 提供，不是民族文化事实或正式评测集。数据服务默认会写此文件；自用前可复制到自己的位置修改 npm 启动参数。不要提交用户输入和运行结果。内置知识与模板仅作源码演示，未经文化准确性验收。

第三方说明见 THIRD_PARTY_NOTICES.md；源提交、文件和校验见 RELEASE_MANIFEST.json、SHA256SUMS。
