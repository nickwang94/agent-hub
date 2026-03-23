# 学习笔记 - 从零开始构建多 Agent 系统

## 项目概述

这是一个教学性质的项目，带你从头开始构建一个基于 LangChain 和 LangGraph 的多 Agent 协作系统。

## 核心概念

### 1. 什么是 Agent？

Agent = LLM + 记忆 + 工具

在这个项目中，Agent 是一个能够：
- 接收用户输入
- 处理并生成响应
- 保持对话历史记忆
的智能体

### 2. 什么是 LangChain？

LangChain 是一个框架，让你可以：
- 统一调用不同的 LLM（如 Qwen、Claude、GPT-4）
- 管理提示词（Prompt）
- 构建复杂的链式调用
- 创建 Agent

### 3. 什么是 LangGraph？

LangGraph 是基于图的状态机，用于：
- 定义多 Agent 工作流
- 管理状态流转
- 实现路由和条件分支

**核心思想**：把 Agent 协作看成一个图，每个 Agent 是一个节点，消息在节点间流动

### 4. 什么是 RAG？

RAG = Retrieval-Augmented Generation（检索增强生成）

流程：
```
用户问题 → 检索知识库 → 找到相关文档 → 连同文档一起问 LLM → 获得有依据的回答
```

## 代码结构解析

### 核心模块 (core/)

```
core/config.py  - 配置管理（API Key、模型名称等）
core/llm.py     - LLM 客户端封装（统一接口）
```

**学习点**：如何封装 LLM 调用，使得切换模型很方便

### Agent 模块 (agents/)

```
agents/base.py      - 基础 Agent 类（抽象接口）
agents/chat.py      - 对话 Agent（通用聊天）
agents/researcher.py - 研究 Agent（知识库问答）
```

**学习点**：
- 如何使用继承和多态
- 如何让 Agent 保持记忆
- 如何调用 LLM 生成响应

### 知识库模块 (knowledge/)

```
knowledge/store.py  - 向量存储（ChromaDB）
knowledge/loader.py - 文档加载和分割
```

**学习点**：
- 什么是向量数据库
- 如何将文本分割成块
- 如何进行相似度搜索

### Session 模块 (session/)

```
session/manager.py - 会话管理
```

**学习点**：
- 如何管理多个对话会话
- 如何实现会话过期
- 如何限制消息数量

### 编排器 (orchestrator.py)

```
orchestrator.py - LangGraph 状态机，协调多 Agent 协作
```

**学习点**：
- 如何定义状态（AgentState）
- 如何定义节点（router、chat、researcher）
- 如何实现条件路由

## LangGraph 核心代码解析

### 1. 定义状态

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    current_agent: str
    user_input: str
    response: str
```

**解释**：
- `messages`: 对话历史，使用 `operator.add` 表示每次追加新消息
- `current_agent`: 当前选中的 Agent
- `user_input`: 用户输入
- `response`: 最终响应

### 2. 构建状态图

```python
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("router", self._router_node)
workflow.add_node("chat", self._chat_node)
workflow.add_node("researcher", self._researcher_node)

# 设置入口
workflow.add_edge(START, "router")

# 条件路由
workflow.add_conditional_edges(
    "router",
    self._route_agent,
    {"chat": "chat", "researcher": "researcher"},
)

# 完成处理
workflow.add_edge("chat", END)
workflow.add_edge("researcher", END)
```

**流程图**：
```
START → router → (判断) → chat → END
                      → researcher → END
```

### 3. 运行状态图

```python
final_state = self.graph.invoke(initial_state)
```

## 运行步骤

### 1. 获取 API Key

访问 https://bailian.console.aliyun.com/ 获取 API Key

### 2. 配置环境

```bash
# 编辑 .env 文件
DASHSCOPE_API_KEY=sk-your-key-here
LLM_MODEL=qwen-plus
```

### 3. 运行程序

```bash
cd /Users/nickwang/Documents/application/agent-hub
source venv/bin/activate
python main.py
```

### 4. 测试对话

```
你：你好
AI (对话): 你好！有什么可以帮助你的？

你：查询知识库中关于 Python 的内容
AI (研究): 抱歉，知识库中暂无相关信息
（提示：先使用 /load 命令加载文档）
```

## 扩展练习

### 练习 1：添加新的 Agent

创建一个翻译 Agent：

```python
# agents/translator.py
from .base import BaseAgent

class TranslatorAgent(BaseAgent):
    def invoke(self, message: str, context=None) -> str:
        prompt = f"请将以下内容翻译成英文：{message}"
        # 调用 LLM
        return response
```

### 练习 2：修改路由逻辑

让包含"翻译"关键词的请求使用翻译 Agent：

```python
def _router_node(self, state):
    if "翻译" in state["user_input"]:
        state["current_agent"] = "translator"
    # ...
```

### 练习 3：加载真实文档

```bash
# 在程序中
/load /path/to/your/document.txt
```

## 下一步学习

1. **深入 LangChain**: https://python.langchain.com/
2. **学习 LangGraph**: https://langchain-ai.github.io/langgraph/
3. **了解 ChromaDB**: https://docs.trychroma.com/
4. **学习 RAG 技术**: 检索增强生成

## 常见问题

### Q: 为什么使用 OpenAI 接口调用 Qwen？
A: 阿里百炼提供了兼容 OpenAI 格式的接口，可以使用相同的 SDK 调用不同模型，方便切换

### Q: ChromaDB 是做什么的？
A: 轻量级向量数据库，用于存储文档的嵌入向量，支持相似度搜索

### Q: 如何 debug？
A: 在代码中添加 `print` 语句，查看状态流转和变量值
