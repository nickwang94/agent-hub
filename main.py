"""
主入口 - CLI 界面

提供命令行交互界面
"""
import os
from pathlib import Path

# 确保项目路径在 sys.path 中
project_root = Path(__file__).parent
import sys
sys.path.insert(0, str(project_root))

from orchestrator import AgentOrchestrator
from session.manager import SessionManager
from knowledge.store import KnowledgeStore
from knowledge.loader import DocumentLoader
from agents.chat import ChatAgent
from agents.researcher import ResearcherAgent
from core.config import Config


def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("多 Agent 协作系统 - LangChain + LangGraph")
    print("=" * 60)
    print()
    print("命令:")
    print("  /help     - 显示帮助")
    print("  /new      - 新建会话")
    print("  /history  - 查看历史消息")
    print("  /clear    - 清空当前会话")
    print("  /status   - 显示系统状态")
    print("  /load     - 加载文档到知识库")
    print("  /quit     - 退出程序")
    print()
    print("提示：包含'查询'、'搜索'、'知识库'等词将使用研究 Agent")
    print("-" * 60)


def print_help():
    """打印帮助信息"""
    print("""
可用命令:
  /help      - 显示此帮助信息
  /new       - 创建新的会话
  /history   - 查看当前会话的历史消息
  /clear     - 清空当前会话的消息
  /status    - 显示系统状态（会话数、知识库文档数等）
  /load      - 加载文档文件到知识库（用法：/load <文件路径>）
  /agents    - 显示可用的 Agent 信息
  /quit      - 退出程序

对话提示:
  - 直接输入文字进行对话
  - 包含"查询"、"搜索"、"知识库"等关键词会自动使用研究 Agent
  - 研究 Agent 会从知识库中检索相关信息来回答问题
    """)


def load_document(orchestrator: AgentOrchestrator, file_path: str):
    """加载文档到知识库"""
    path = Path(file_path)

    if not path.exists():
        print(f"错误：文件不存在 - {file_path}")
        return

    print(f"正在加载文件：{file_path}...")

    # 初始化加载器和存储
    loader = DocumentLoader()
    store = KnowledgeStore()

    # 加载文档
    documents = loader.load_from_file(str(path))

    # 添加到知识库
    if documents:
        store.add_documents(
            documents=[d["content"] for d in documents],
            ids=[d["id"] for d in documents],
            metadatas=[d["metadata"] for d in documents],
        )
        print(f"成功加载 {len(documents)} 个文档块到知识库！")

        # 更新研究 Agent 的知识库
        if orchestrator.researcher_agent:
            orchestrator.researcher_agent.set_knowledge_store(store)
    else:
        print("警告：未从文件中提取到内容")


def main():
    """主函数"""
    # 验证配置
    if not Config.DASHSCOPE_API_KEY or Config.DASHSCOPE_API_KEY == "your-api-key-here":
        print("错误：请先配置 DASHSCOPE_API_KEY")
        print(f"请复制 .env.example 为 .env 并填入你的 API Key")
        print(f"文件位置：{Path(__file__).parent / '.env'}")
        return

    # 初始化组件
    session_manager = SessionManager()

    # 初始化知识库
    knowledge_store = KnowledgeStore()

    # 初始化 Agent
    chat_agent = ChatAgent()
    researcher_agent = ResearcherAgent(knowledge_store=knowledge_store)

    # 初始化编排器
    orchestrator = AgentOrchestrator(
        chat_agent=chat_agent,
        researcher_agent=researcher_agent,
        session_manager=session_manager,
    )

    # 当前会话 ID
    current_session_id = None

    # 打印欢迎信息
    print_welcome()

    # 主循环
    while True:
        try:
            # 获取用户输入
            user_input = input("\n你：").strip()

            if not user_input:
                continue

            # 处理命令
            if user_input.startswith("/"):
                command = user_input.lower().split()[0]

                if command == "/quit":
                    print("再见！")
                    break

                elif command == "/help":
                    print_help()

                elif command == "/new":
                    current_session_id = None
                    print("已创建新会话")

                elif command == "/clear":
                    if current_session_id:
                        session_manager.delete_session(current_session_id)
                        current_session_id = None
                    print("会话已清空")

                elif command == "/history":
                    session = session_manager.get_session(current_session_id)
                    if session and session.messages:
                        print("\n--- 历史消息 ---")
                        for msg in session.messages[-10:]:  # 显示最近 10 条
                            role = "你" if isinstance(msg, type(msg).__name__) == "HumanMessage" else "AI"
                            print(f"{role}: {msg.content[:100]}...")
                    else:
                        print("暂无历史消息")

                elif command == "/status":
                    stats = session_manager.get_stats()
                    doc_count = knowledge_store.get_document_count()
                    print(f"\n系统状态:")
                    print(f"  活跃会话数：{stats['total_sessions']}")
                    print(f"  知识库文档数：{doc_count}")
                    if current_session_id:
                        print(f"  当前会话：{current_session_id[:8]}...")

                elif command == "/load":
                    parts = user_input.split(maxsplit=1)
                    if len(parts) < 2:
                        print("用法：/load <文件路径>")
                    else:
                        load_document(orchestrator, parts[1])

                elif command == "/agents":
                    info = orchestrator.get_agent_info()
                    print("\n可用 Agent:")
                    for name, state in info.items():
                        print(f"  - {name}: {state['description']}")

                else:
                    print(f"未知命令：{command}，输入 /help 查看帮助")

                continue

            # 处理普通消息
            response, agent_used = orchestrator.process_message(
                message=user_input,
                session_id=current_session_id,
            )

            # 更新会话 ID
            if current_session_id is None:
                current_session_id = orchestrator.session_manager.list_sessions()[0]["id"]

            # 显示响应
            agent_label = "(研究)" if agent_used == "researcher" else "(对话)"
            print(f"\nAI {agent_label}: {response}")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误：{e}")


if __name__ == "__main__":
    main()
