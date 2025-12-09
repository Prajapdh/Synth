import sys
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import Agent
from core.planner import PlannerAgent

load_dotenv()

def main():
    PROJECT_NAME = "saucedemo"
    GOAL = "Go to https://saucedemo.com, Login as standard_user(username: standard_user and password: secret_sauce) and add the first item to the cart."
    
    print(f"Goal: {GOAL}")
    
    # 1. PLAN
    print("\n--- PHASE 1: PLANNING ---")
    planner = PlannerAgent(model_provider="openai", project_name=PROJECT_NAME)
    steps = planner.plan(GOAL)
    
    print("Generated Plan:")
    for i, step in enumerate(steps):
        print(f"{i+1}. {step}")
        
    # 2. EXECUTE
    print("\n--- PHASE 2: EXECUTION ---")
    # We reuse the same worker agent for all steps to maintain browser session
    worker = Agent(model_provider="openai", project_name=PROJECT_NAME)
    
    for i, step in enumerate(steps):
        print(f"\n>> Executing Step {i+1}: {step}")
        
        state = {
            "messages": [HumanMessage(content=step)],
            "screenshot": "",
            "items": [],
            "goal": step
        }
        
        # Run until done
        for event in worker.app.stream(state):
            for key, value in event.items():
                print(f"   [{key}] ...")

if __name__ == "__main__":
    main()
