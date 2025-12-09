import sys
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import Agent

load_dotenv()

def main():
    PROJECT_NAME = "saucedemo"
    # Goal that requires verification: "Ensure the cart has 1 item"
    # The agent should: 1. Add item 2. Check badge.
    GOAL = "Login as standard_user and ensure the shopping cart has exactly 1 item."
    
    print(f"Goal: {GOAL}")
    
    worker = Agent(model_provider="openai", project_name=PROJECT_NAME)
    
    state = {
        "messages": [HumanMessage(content=GOAL)],
        "screenshot": "",
        "items": [],
        "goal": GOAL
    }
    
    # Run until done
    for event in worker.app.stream(state):
        for key, value in event.items():
            print(f"   [{key}] ...")

if __name__ == "__main__":
    main()
