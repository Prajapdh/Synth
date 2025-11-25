import os
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.tools import get_tools, get_browser

class Agent:
    def __init__(self, model_provider="openai"):
        self.tools = get_tools()
        self.browser = get_browser()
        
        # Initialize Model
        if model_provider == "openai":
            self.model = ChatOpenAI(model="gpt-4o", temperature=0)
        elif model_provider == "anthropic":
            self.model = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
        else:
            raise ValueError("Invalid model provider")

        self.model = self.model.bind_tools(self.tools)

        # Build Graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)

        workflow.set_entry_point("agent")
        
        # Conditional Edge: If tool calls -> tools, else -> END
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        workflow.add_edge("tools", "agent")
        
        self.app = workflow.compile()

    def should_continue(self, state: AgentState):
        messages = state['messages']
        last_message = messages[-1]
        
        if not last_message.tool_calls:
            return "end"
        
        # Check if 'done' tool was called
        if any(tc['name'] == 'done' for tc in last_message.tool_calls):
            return "end"
            
        return "continue"

    def call_model(self, state: AgentState):
        messages = state['messages']
        
        # 1. Capture State (Eyes)
        # Only capture if we are not just returning from a tool execution 
        # (Optimization: In a real loop we might want to see the result of the action immediately)
        # For this prototype, we capture every time the model thinks.
        if self.browser.page:
            print("Capturing state...")
            vision_state = self.browser.capture_state()
            screenshot = vision_state['screenshot']
            items = vision_state['items']
            
            # Create System Message with Context
            # We format the item map as text for the LLM
            item_text = "\n".join([
                f"ID: {i['id']} | Tag: {i['tag']} | Text: {i['text']}" 
                for i in items
            ])
            
            system_prompt = f"""
            You are an autonomous QA Agent.
            Your goal is to accomplish the user's objective on the web page.
            
            You have access to a browser.
            The current page has been analyzed and interactive elements are marked with numeric IDs.
            
            INTERACTIVE ELEMENTS:
            {item_text}
            
            INSTRUCTIONS:
            1. Analyze the user's goal and the list of elements.
            2. Decide which element to interact with.
            3. Call the appropriate tool (click_element, type_text, etc.) using the ID.
            4. If the goal is met, call the 'done' tool.
            """
            
            # Add image to the message (Multimodal)
            # Note: LangChain format for images varies by provider. 
            # This is a simplified generic approach for GPT-4o.
            user_msg = HumanMessage(
                content=[
                    {"type": "text", "text": "Here is the current screen."},
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/png;base64,{screenshot}"}
                    }
                ]
            )
            
            # Prepend system prompt to history (or update it)
            # For simplicity, we just pass it as a separate message here
            full_history = [SystemMessage(content=system_prompt)] + messages + [user_msg]
            
            # DEBUG: Write to file
            with open("debug_messages.txt", "w", encoding="utf-8") as f:
                for i, m in enumerate(full_history):
                    f.write(f"Index: {i} | Role: {m.type}\n")
                    f.write(f"Content: {str(m.content)[:100]}...\n")
                    if hasattr(m, 'tool_calls') and m.tool_calls:
                        f.write(f"Tool Calls: {m.tool_calls}\n")
                    if hasattr(m, 'tool_call_id'):
                        f.write(f"Tool Call ID: {m.tool_call_id}\n")
                    f.write("-" * 20 + "\n")

            response = self.model.invoke(full_history)
        else:
            # Browser not started yet, just let the model decide to navigate
            response = self.model.invoke(messages)

        return {"messages": [response]}

    def tool_node(self, state: AgentState):
        messages = state['messages']
        last_message = messages[-1]
        
        outputs = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            # Find and invoke tool
            tool = next(t for t in self.tools if t.name == tool_name)
            result = tool.invoke(tool_args)  # Execute the tool to get the result
            
            # Add tool output as a ToolMessage (NOT as a raw string)
            from langchain_core.messages import ToolMessage
            outputs.append(ToolMessage(tool_call_id=tool_call['id'], content=str(result)))
            
        return {"messages": outputs}
