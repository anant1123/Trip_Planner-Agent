"""
TripGenie Agent - Core AI logic with LangGraph
"""
from typing import List
import time

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Annotated, TypedDict

from config.settings import settings
from config.prompts import SYSTEM_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)


class AgentState(TypedDict):
    """Agent state with message history"""
    messages: Annotated[list[BaseMessage], add_messages]


class TripGenieAgent:
    """Main TripGenie Agent class"""
    
    def __init__(self):
        """Initialize the TripGenie agent"""
        logger.info("Initializing TripGenie Agent...")
        
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.app = self._build_graph()
        
        logger.info("TripGenie Agent initialized successfully")
    
    def _initialize_llm(self) -> ChatGroq:
        """Initialize the language model"""
        try:
            llm = ChatGroq(
                model=settings.model.model_name,
                temperature=settings.model.temperature,
                max_retries=settings.model.max_retries,
                api_key=settings.api.groq_api_key,
                timeout=settings.model.timeout
            )
            logger.info(f"LLM initialized: {settings.model.model_name}")
            return llm
        except Exception as e:
            logger.error("Failed to initialize LLM", exc=e)
            raise
    
    def _initialize_tools(self) -> List:
        """Initialize search tools"""
        tools = []
        
        try:
            # Primary: Tavily
            tavily = TavilySearchResults(
                max_results=settings.search.tavily_max_results,
                api_key=settings.api.tavily_api_key,
                description=(
                    "Primary search tool for real-time travel information. "
                    "Use this to find flight prices, hotel availability, "
                    "restaurant recommendations, and current travel advisories. "
                    "Always cite this tool when using its results."
                )
            )
            tools.append(tavily)
            logger.info("Tavily search tool initialized")
            
            # Fallback: DuckDuckGo
            if settings.search.enable_ddg_fallback:
                ddg = DuckDuckGoSearchRun(
                    description=(
                        "Fallback search tool for general information. "
                        "Use only if Tavily returns no results or for "
                        "general knowledge queries about destinations."
                    )
                )
                tools.append(ddg)
                logger.info("DuckDuckGo fallback tool initialized")
            
        except Exception as e:
            logger.error("Failed to initialize tools", exc=e)
            raise
        
        return tools
    
    def _agent_node(self, state: AgentState) -> dict:
        """
        Main agent reasoning node
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with new message
        """
        try:
            messages = state["messages"]
            
            # Add system prompt if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            
            # Invoke LLM
            logger.debug("Invoking LLM with tools")
            response = self.llm_with_tools.invoke(messages)
            
            return {"messages": [response]}
            
        except Exception as e:
            logger.error("Agent node error", exc=e)
            # Return error message instead of crashing
            error_msg = AIMessage(
                content=(
                    f"I encountered an error while processing your request: {str(e)}. "
                    "Please try again or rephrase your query."
                )
            )
            return {"messages": [error_msg]}
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        try:
            workflow = StateGraph(AgentState)
            
            # Add nodes
            workflow.add_node("agent", self._agent_node)
            workflow.add_node("tools", ToolNode(self.tools))
            
            # Add edges
            workflow.add_edge(START, "agent")
            workflow.add_conditional_edges("agent", tools_condition)
            workflow.add_edge("tools", "agent")
            
            app = workflow.compile()
            logger.info("LangGraph workflow compiled successfully")
            return app
            
        except Exception as e:
            logger.error("Failed to build graph", exc=e)
            raise
    
    def generate_trip_plan(self, query: str) -> str:
        """
        Generate trip plan from query
        
        Args:
            query: User's travel planning query
            
        Returns:
            Trip plan as string
        """
        logger.info("Generating trip plan")
        start_time = time.time()
        
        try:
            initial_state = {"messages": [HumanMessage(content=query)]}
            result = self.app.invoke(initial_state)
            
            final_message = result["messages"][-1]
            content = final_message.content if isinstance(final_message, AIMessage) else str(final_message)
            
            duration = time.time() - start_time
            logger.log_api_call("trip_generation", "success", duration)
            logger.info(f"Trip plan generated successfully in {duration:.2f}s")
            
            return content
            
        except Exception as e:
            duration = time.time() - start_time
            logger.log_api_call("trip_generation", "failed", duration)
            logger.error("Failed to generate trip plan", exc=e)
            return f"Error: Unable to generate trip plan. {str(e)}"
    
    def stream_trip_plan(self, query: str):
        """
        Stream trip plan generation
        
        Args:
            query: User's travel planning query
            
        Yields:
            Messages as they're generated
        """
        logger.info("Streaming trip plan generation")
        
        try:
            initial_state = {"messages": [HumanMessage(content=query)]}
            
            for event in self.app.stream(initial_state, stream_mode="values"):
                message = event["messages"][-1]
                
                # Skip system and human messages
                if not isinstance(message, (HumanMessage, SystemMessage)):
                    yield message
                    
        except Exception as e:
            logger.error("Failed to stream trip plan", exc=e)
            yield AIMessage(content=f"Error: {str(e)}")
