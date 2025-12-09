from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import List

from core.knowledge import KnowledgeManager

class Plan(BaseModel):
    steps: List[str] = Field(description="List of sequential steps to achieve the goal")

class PlannerAgent:
    def __init__(self, model_provider="openai", project_name=None):
        self.knowledge = None
        if project_name:
            self.knowledge = KnowledgeManager(project_name)
            
        # Initialize Model
        if model_provider == "openai":
            self.model = ChatOpenAI(model="gpt-4o", temperature=0)
        elif model_provider == "anthropic":
            self.model = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
        else:
            raise ValueError("Invalid model provider")
            
        # Force structured output
        self.model = self.model.with_structured_output(Plan)

    def plan(self, goal: str) -> List[str]:
        knowledge_context = ""
        if self.knowledge:
            knowledge_context = f"\nPROJECT KNOWLEDGE:\n{self.knowledge.get_knowledge()}\n"
            
        system_prompt = f"""
        You are a QA Lead Planner.
        Your goal is to break down a high-level test ticket into small, executable steps for a junior QA bot.
        
        {knowledge_context}
        
        INSTRUCTIONS:
        1. Analyze the ticket/goal.
        2. Break it down into clear, sequential steps.
        3. Each step should be actionable (e.g., "Go to login page", "Enter credentials", "Click checkout").
        4. Keep steps granular but not too low-level.
        """
        
        response = self.model.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=goal)
        ])
        
        return response.steps
