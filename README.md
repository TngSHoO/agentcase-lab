# AgentCase Lab

面向 AI 产品和应用团队的智能体故障复盘与根因分析平台。

它把一次 Agent 运行拆解为可回放的执行轨迹，帮助团队定位提示词、知识检索、工具调用、上下文、长期记忆、权限或模型幻觉问题，并比较修复前后的成功率、延迟、Token 和成本。

> 当前仓库是作品集 MVP。内置案例为明确标识的模拟数据，不代表任何模型的真实公开排名或生产效果。

## 核心功能

- 数据看板：成功率、修复率、根因分布、延迟与成本
- 故障案例：按场景、状态和根因筛选
- 轨迹回放：检查用户输入、计划、工具、记忆、模型和最终结果
- 根因分析：演示规则模式，以及可选的 OpenAI 兼容模型分析
- 版本对比：验证修复前后的任务状态和关键指标

## 快速开始

需要 Python 3.11 或更高版本。

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

打开 `http://localhost:8501`。首次启动会自动创建 SQLite 数据库并写入 30 条演示案例。

## 可选：启用实时 AI 根因分析

复制 `.env.example` 为 `.env`，填入 OpenAI 兼容服务的配置：

```text
AGENTCASE_API_KEY=你的密钥
AGENTCASE_API_BASE=https://api.deepseek.com/v1
AGENTCASE_MODEL=deepseek-chat
```

不要将 `.env` 或真实 API Key 提交到 GitHub。

## 测试

```powershell
python -m pip install -r requirements-dev.txt
pytest
ruff check .
```

## 项目结构

```text
agentcase-lab/
├── app.py                 # 产品首页
├── pages/                 # 五个核心页面
├── agentcase/             # 数据模型、SQLite、指标与分析逻辑
├── data/                  # 运行时生成的本地数据库
├── docs/                  # PRD、用户旅程、指标和决策记录
└── tests/                 # 自动化测试
```

## 产品文档

- [PRD](docs/PRD.md)
- [用户旅程](docs/USER_JOURNEY.md)
- [指标体系](docs/METRICS.md)
- [产品决策](docs/PRODUCT_DECISIONS.md)

## 开发说明

本项目为从零搭建的个人作品集项目，开发过程中使用了 AI 编程工具辅助实现。产品定义、范围取舍、指标设计、验收和最终内容应由项目维护者理解并负责。

## License

建议在正式发布前根据个人需求选择并添加许可证。若希望他人自由使用和修改，可选择 MIT License。
