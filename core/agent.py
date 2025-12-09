import os
import base64
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import AgentState
from core.tools import get_tools, get_browser

from core.knowledge import KnowledgeManager

class Agent:
    def __init__(self, model_provider="openai", project_name=None):
        self.tools = get_tools()
        self.browser = get_browser()
        self.knowledge = None
        self.screenshot_cnt = 0
        
        if project_name:
            self.knowledge = KnowledgeManager(project_name)
        
        # Initialize Model
        if model_provider == "openai":
            self.model = ChatOpenAI(model="gpt-4o", temperature=0)
        elif model_provider == "anthropic":
            self.model = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
        else:
            raise ValueError("Invalid model provider")
        
        print("Model initialized")

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
        print("Agent initialized")

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
        print("Call Model Invoked")
        messages = state['messages']
        
        # 1. Capture State (Eyes)
        if self.browser.page:
            print("Capturing state...")
            vision_state = self.browser.capture_state()
            screenshot = vision_state['screenshot']
            #save all screenshots in a folder without getting permission error
            with open(f"screenshots/screenshot_{self.screenshot_cnt}.png", "wb") as f:
                f.write(base64.b64decode(screenshot)) 
            self.screenshot_cnt += 1

            items = vision_state['items']
            
            # Create System Message with Context
            item_text = "\n".join([
                f"ID: {i['id']} | Tag: {i['tag']} | Text: {i['text']}" 
                for i in items
            ])
            
            # Get Project Knowledge
            knowledge_context = ""
            if self.knowledge:
                k_text = self.knowledge.get_knowledge()
                creds = self.knowledge.config.get('credentials', {})
                c_text = f"CREDENTIALS: {creds}" if creds else ""
                
                knowledge_context = f"\nPROJECT KNOWLEDGE:\n{k_text}\n\n{c_text}\n"
            
            system_prompt = f"""
            You are an autonomous QA Agent.
            Your goal is to accomplish the user's objective on the web page.
            
            You have access to a browser.
            The current page has been analyzed and interactive elements are marked with numeric IDs.
            
            {knowledge_context}
            
            INTERACTIVE ELEMENTS:
            {item_text}
            
            INSTRUCTIONS:
            1. Analyze the user's goal and the list of elements.
            2. Consult the Project Knowledge for hints (e.g., credentials, flow descriptions).
            3. VERIFICATION: Check if the *previous* action (if any) succeeded. 
               - Did the page change as expected?
               - Did the element react?
               - If it failed, try a DIFFERENT strategy (e.g., different element, different tool).
            4. Decide which element to interact with.
            5. Call the appropriate tool (click_element, type_text, etc.) using the ID.
            6. If the goal is met, call the 'done' tool.
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
            print("Browser not started yet, just let the model decide to navigate")
            
            # Helper to get project context
            knowledge_context = ""
            if self.knowledge:
                k_text = self.knowledge.get_knowledge()
                creds = self.knowledge.config.get('credentials', {})
                c_text = f"CREDENTIALS: {creds}" if creds else ""
                knowledge_context = f"\nPROJECT KNOWLEDGE:\n{k_text}\n\n{c_text}\n"

            initial_prompt = f"""
            You are an autonomous QA Agent.
            Your goal is to accomplish the user's objective on the web page.
            
            {knowledge_context}
            
            Current State: The browser is not open.
            INSTRUCTIONS:
            1. Analyze the user's goal.
            2. Call the 'navigate' tool to go to the correct URL (check Project Knowledge for base URL).
            """
            
            response = self.model.invoke([SystemMessage(content=initial_prompt)] + messages)

        return {"messages": [response]}

    def tool_node(self, state: AgentState):
        print("Tool Node Invoked")
        messages = state['messages']
        last_message = messages[-1]
        
        outputs = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            # Find tool
            tool = next(t for t in self.tools if t.name == tool_name)
            
            try:
                # Execute tool
                result = tool.invoke(tool_args)
            except Exception as e:
                result = f"Error executing tool {tool_name}: {str(e)}"
            
            # Add tool output message
            # (In a real implementation we need to construct ToolMessage properly)
            # For this prototype we rely on LangGraph's built-in handling or manual construction
            from langchain_core.messages import ToolMessage
            outputs.append(ToolMessage(tool_call_id=tool_call['id'], content=str(result)))
            
        return {"messages": outputs}
