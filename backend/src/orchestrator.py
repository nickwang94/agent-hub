"""
Multi-Agent Orchestrator

Uses LangGraph to build state machine for coordinating multiple agents
"""
from typing import TypedDict, Literal, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

from agents.chat import ChatAgent
from agents.researcher import ResearcherAgent
from session.manager import SessionManager, Session


# ============ State Definitions ============

class AgentState(TypedDict):
    """
    Agent State Definition

    LangGraph uses state to pass information between nodes
    """
    messages: Annotated[list[BaseMessage], operator.add]
    # Current selected agent
    current_agent: str
    # User input
    user_input: str
    # Final response
    response: str


# ============ Routing Logic ============

class AgentOrchestrator:
    """
    Agent Orchestrator

    Uses LangGraph to manage multi-agent collaboration workflow
    """

    # Agent types
    CHAT_AGENT = "chat"
    RESEARCHER_AGENT = "researcher"

    def __init__(
        self,
        chat_agent: ChatAgent = None,
        researcher_agent: ResearcherAgent = None,
        session_manager: SessionManager = None,
    ):
        """
        Initialize orchestrator

        Args:
            chat_agent: Chat Agent
            researcher_agent: Researcher Agent
            session_manager: Session Manager
        """
        self.chat_agent = chat_agent or ChatAgent()
        self.researcher_agent = researcher_agent or ResearcherAgent()
        self.session_manager = session_manager or SessionManager()

        # Build state graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build state graph

        Returns:
            StateGraph: Compiled state graph
        """
        # Create state graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("router", self._router_node)
        workflow.add_node("chat", self._chat_node)
        workflow.add_node("researcher", self._researcher_node)

        # Set entry point
        workflow.add_edge(START, "router")

        # Add conditional edges (routing)
        workflow.add_conditional_edges(
            "router",
            self._route_agent,
            {
                self.CHAT_AGENT: "chat",
                self.RESEARCHER_AGENT: "researcher",
            },
        )

        # End after processing
        workflow.add_edge("chat", END)
        workflow.add_edge("researcher", END)

        # Compile graph
        return workflow.compile()

    def _router_node(self, state: AgentState) -> AgentState:
        """
        Router node

        Analyzes user input to decide which agent to use
        """
        # Simple routing logic: can use keywords to determine
        user_input = state["user_input"].lower()

        # If question contains research/knowledge/document keywords, use Researcher Agent
        research_keywords = [
            "查询", "搜索", "知识库", "文档", "研究",
            "find", "search", "knowledge", "document", "research",
        ]

        if any(keyword in user_input for keyword in research_keywords):
            state["current_agent"] = self.RESEARCHER_AGENT
        else:
            state["current_agent"] = self.CHAT_AGENT

        return state

    def _route_agent(self, state: AgentState) -> Literal["chat", "researcher"]:
        """Routing decision"""
        return state["current_agent"]

    def _chat_node(self, state: AgentState) -> AgentState:
        """
        Chat node

        Uses Chat Agent to process request
        """
        response = self.chat_agent.invoke(
            message=state["user_input"],
            context=state["messages"],
        )

        state["response"] = response
        state["messages"].append(HumanMessage(content=state["user_input"]))
        state["messages"].append(AIMessage(content=response))

        return state

    def _researcher_node(self, state: AgentState) -> AgentState:
        """
        Researcher node

        Uses Researcher Agent to process request
        """
        response = self.researcher_agent.invoke(
            message=state["user_input"],
            context=state["messages"],
        )

        state["response"] = response
        state["messages"].append(HumanMessage(content=state["user_input"]))
        state["messages"].append(AIMessage(content=response))

        return state

    def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Process user message

        Args:
            message: User input
            session_id: Session ID

        Returns:
            tuple[str, str]: (response content, agent name used)
        """
        # Get or create session
        session = self.session_manager.get_or_create_session(session_id)

        # Initial state
        initial_state = AgentState(
            messages=session.get_messages(),
            current_agent="",
            user_input=message,
            response="",
        )

        # Run state graph
        final_state = self.graph.invoke(initial_state)

        # Update session
        session.add_message("user", message)
        session.add_message("assistant", final_state["response"])

        return final_state["response"], final_state["current_agent"]

    def get_agent_info(self) -> dict:
        """Get all agent information"""
        return {
            self.CHAT_AGENT: self.chat_agent.get_state(),
            self.RESEARCHER_AGENT: self.researcher_agent.get_state(),
        }
