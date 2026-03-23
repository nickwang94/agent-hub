# Agent Hub - 多 Agent 协作系统

一个基于 LangChain 和 LangGraph 的多 Agent 协作系统，用于学习 AI Agent 开发。

## 功能特性

- **对话 Agent**: 通用对话交互
- **研究 Agent**: 基于知识库的问答
- **Session 管理**: 多会话支持和历史管理
- **多 Agent 编排**: 使用 LangGraph 实现智能路由
- **知识库**: 支持文档加载和向量检索

## 项目结构

```
agent-hub/
├── core/              # 核心模块
│   ├── config.py      # 配置管理
│   └── llm.py         # LLM 客户端
├── agents/            # Agent 定义
│   ├── base.py        # 基础 Agent 类
│   ├── chat.py        # 对话 Agent
│   └── researcher.py  # 研究 Agent
├── knowledge/         # 知识库
│   ├── store.py       # ChromaDB 向量存储
│   └── loader.py      # 文档加载器
├── session/           # Session 管理
│   └── manager.py     # 会话管理器
├── orchestrator.py    # 多 Agent 编排 (LangGraph)
├── main.py           # CLI 入口
└── pyproject.toml    # 项目配置
```

## 快速开始

### 1. 安装依赖

```bash
cd agent-hub
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

或者手动安装：

```bash
pip install langchain langchain-openai langgraph chromadb python-dotenv pypdf
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的阿里百炼 API Key：

```
DASHSCOPE_API_KEY=your-api-key-here
LLM_MODEL=qwen-plus
```

获取 API Key: https://bailian.console.aliyun.com/

### 3. 运行程序

```bash
python main.py
```

## 使用指南

### 基本对话

直接输入文字即可与对话 Agent 交互：

```
你：你好，介绍一下你自己
AI (对话): 你好！我是一个 AI 助手...
```

### 知识库问答

使用关键词（查询、搜索、知识库等）会自动切换到研究 Agent：

```
你：查询知识库中关于 Python 的内容
AI (研究): 根据知识库内容，Python 是一种...
```

### 加载文档到知识库

```
/load <文件路径>
```

支持 .txt, .md, .pdf 等格式。

### 常用命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助 |
| `/new` | 新建会话 |
| `/history` | 查看历史消息 |
| `/clear` | 清空当前会话 |
| `/status` | 显示系统状态 |
| `/load` | 加载文档到知识库 |
| `/agents` | 显示可用 Agent |
| `/quit` | 退出程序 |

## 核心概念讲解

### 1. LangChain 是什么？

LangChain 是一个用于开发 LLM 应用的框架，提供了：
- **Model I/O**: 统一的 LLM 接口
- **Prompts**: 提示词管理
- **Chains**: 链式调用
- **Agents**: 自主决策的 LLM 调用

### 2. LangGraph 是什么？

LangGraph 是 LangChain 出品的基于图的状态机库，用于：
- 构建复杂的多 Agent 工作流
- 实现有状态的决策流程
- 支持循环和条件分支

### 3. Agent 架构

```
用户输入 → Router(路由) → Chat Agent 或 Researcher Agent → 输出
```

### 4. 向量知识库

```
文档 → 分割 → Embedding → 向量存储 → 相似度检索 → RAG 回答
```

## 学习路线

1. **第一步**: 理解 `agents/base.py` - 基础 Agent 接口设计
2. **第二步**: 理解 `agents/chat.py` - 如何与 LLM 对话
3. **第三步**: 理解 `knowledge/` - 向量数据库的使用
4. **第四步**: 理解 `orchestrator.py` - LangGraph 状态机
5. **第五步**: 扩展新的 Agent 类型

## 扩展开发

### 添加新的 Agent

1. 继承 `BaseAgent` 类
2. 实现 `invoke` 方法
3. 在 `orchestrator.py` 中添加路由逻辑

```python
from agents.base import BaseAgent

class MyCustomAgent(BaseAgent):
    def invoke(self, message: str, context=None) -> str:
        # 你的逻辑
        return "response"
```

### 修改路由逻辑

编辑 `orchestrator.py` 中的 `_router_node` 方法，添加自定义的路由判断。

## 调试技巧

1. 在 `.env` 中设置更小的模型以节省成本
2. 使用 `print` 语句调试状态流转
3. 查看 LangGraph 的可视化图：`graph.get_graph().draw_mermaid()`

## 参考资源

- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [ChromaDB 文档](https://docs.trychroma.com/)

## License

MIT
