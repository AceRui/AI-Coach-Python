# AI Coach - 多智能体健身教练系统

基于LlamaIndex框架构建的智能健身教练系统，采用多智能体架构，为用户提供个性化的健身指导和服务支持。

## 🌟 项目特色

- **多智能体架构**: 采用专业分工的多智能体系统，每个智能体专注特定领域
- **流式对话**: 支持实时流式响应，提供流畅的对话体验
- **记忆功能**: 基于Redis的用户对话记忆，支持上下文连续对话
- **多语言支持**: 支持中文、英文等多种语言交互
- **个性化定制**: 支持用户健身计划和基本信息的个性化设置

## 📄 项目结构
```
├── app/
│   ├── agent/              # 智能体相关模块
│   │   ├── agent_chat.py   # 对话处理逻辑
│   │   ├── agent_init.py   # 智能体初始化
│   │   ├── agent_llms.py   # LLM配置
│   │   ├── agent_memory.py # 记忆管理
│   │   └── agent_tools.py  # 智能体工具
│   ├── api/                # API接口
│   │   ├── routes.py       # 路由定义
│   │   └── schema.py       # 数据模型
│   ├── db/                 # 数据库相关
│   │   └── redis/          # Redis操作
│   ├── config.py           # 配置管理
│   ├── logger.py           # 日志配置
│   └── main.py             # 应用入口
├── frontend/               # 前端界面
│   └── app.py              # Streamlit应用
├── requirements.txt        # 依赖列表
└── README.md              # 项目说明
```

## 🤖 智能体系统

系统包含5个专业智能体：

### 1. 路由智能体 (Sarah)
- **职责**: 分析用户问题，智能路由到对应的专业智能体
- **功能**: 问题分类、智能体切换、用户引导

### 2. 健身教练智能体
- **职责**: 提供专业的健身指导和建议
- **功能**: 锻炼建议、健身计划修改、老年人专业指导
- **工具**: adjust_workout_plan_tool

### 3. 订阅支持智能体
- **职责**: 处理订阅、付费、退款等商务问题
- **功能**: 订阅状态查询、取消订阅、退款处理

### 4. 技术支持智能体
- **职责**: 解决App使用中的技术问题
- **功能**: 故障排查、技术支持、问题诊断

### 5. 个人定制智能体
- **职责**: 帮助用户修改个人信息和健身计划
- **功能**: 个人信息更新、健身计划定制
- **工具**: adjust_workout_plan_tool, update_basic_information_tool

## 🛠️ 技术栈

- **后端框架**: FastAPI
- **AI框架**: LlamaIndex
- **LLM**: Google Gemini / Ollama
- **数据库**: Redis (用户记忆存储)
- **日志**: Loguru
- **配置管理**: Pydantic Settings

## 📋 系统要求

- Python 3.8+
- Redis Server
- Google API Key (用于Gemini) 或 Ollama (本地部署)

## 🚀 快速开始

### 1. 环境配置

```bash
# 克隆项目
git clone <your-repo-url>
cd AI-Coach-Python

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的配置
```