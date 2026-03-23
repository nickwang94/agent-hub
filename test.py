"""
测试脚本 - 验证项目基本功能

运行前请确保已配置 .env 文件
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.config import Config
from core.llm import create_llm


def test_config():
    """测试配置加载"""
    print("测试配置加载...")
    print(f"  DASHSCOPE_API_KEY: {'已设置' if Config.DASHSCOPE_API_KEY else '未设置'}")
    print(f"  LLM_MODEL: {Config.LLM_MODEL}")
    return True


def test_llm():
    """测试 LLM 连接"""
    print("\n测试 LLM 连接...")

    if not Config.DASHSCOPE_API_KEY or Config.DASHSCOPE_API_KEY == "your-api-key-here":
        print("  跳过：请先在 .env 文件中配置 DASHSCOPE_API_KEY")
        return False

    try:
        llm = create_llm()
        response = llm.invoke("你好，请用一句话介绍你自己")
        print(f"  LLM 响应：{response.content[:50]}...")
        print("  LLM 连接成功!")
        return True
    except Exception as e:
        print(f"  LLM 连接失败：{e}")
        return False


def test_agents():
    """测试 Agent 创建"""
    print("\n测试 Agent 创建...")

    try:
        from agents.chat import ChatAgent
        from agents.researcher import ResearcherAgent

        chat_agent = ChatAgent()
        print(f"  ChatAgent: 创建成功")

        researcher_agent = ResearcherAgent()
        print(f"  ResearcherAgent: 创建成功")

        return True
    except Exception as e:
        print(f"  Agent 创建失败：{e}")
        return False


def test_knowledge_store():
    """测试知识库"""
    print("\n测试知识库...")

    try:
        from knowledge.store import KnowledgeStore

        store = KnowledgeStore()
        count = store.get_document_count()
        print(f"  当前文档数：{count}")

        # 测试添加文档
        store.add_documents(
            documents=["这是一个测试文档"],
            ids=["test-1"],
        )
        print(f"  添加测试文档后：{store.get_document_count()}")

        # 测试搜索
        results = store.search("测试")
        print(f"  搜索结果：{len(results['documents'][0])} 条")

        # 清理测试文档
        store.delete_documents(["test-1"])

        print("  知识库测试成功!")
        return True
    except Exception as e:
        print(f"  知识库测试失败：{e}")
        return False


def test_session():
    """测试 Session 管理"""
    print("\n测试 Session 管理...")

    try:
        from session.manager import SessionManager

        manager = SessionManager()

        # 创建会话
        session = manager.create_session({"test": True})
        print(f"  创建会话：{session.id[:8]}...")

        # 添加消息
        session.add_message("user", "你好")
        session.add_message("assistant", "你好，有什么可以帮助你的？")

        print(f"  消息数：{len(session.messages)}")

        # 获取会话
        retrieved = manager.get_session(session.id)
        print(f"  获取会话：{retrieved.id[:8] if retrieved else '失败'}")

        # 删除会话
        manager.delete_session(session.id)
        print("  Session 管理测试成功!")

        return True
    except Exception as e:
        print(f"  Session 管理测试失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("多 Agent 协作系统 - 功能测试")
    print("=" * 60)

    results = []

    results.append(("配置加载", test_config()))
    results.append(("LLM 连接", test_llm()))
    results.append(("Agent 创建", test_agents()))
    results.append(("知识库", test_knowledge_store()))
    results.append(("Session 管理", test_session()))

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, passed in results:
        status = "通过" if passed else "失败"
        print(f"  {name}: {status}")

    total = sum(1 for _, p in results if p)
    print(f"\n总计：{total}/{len(results)} 通过")


if __name__ == "__main__":
    main()
