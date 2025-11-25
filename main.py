import sys
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import Agent

# Load env vars (API Keys)
load_dotenv()

def main():
    print("Initializing Agent...")
    # You can switch to 'anthropic' if you have that key
    agent = Agent(model_provider="openai") 
    
    goal = "Go to https://saucedemo.com, login with standard_user and secret_sauce, and verify the login."
    print(f"Goal: {goal}")
    
    initial_state = {
        "messages": [HumanMessage(content=goal)],
        "screenshot": "",
        "items": [],
        "goal": goal
    }
    
    print("Starting Agent Loop...")
    for event in agent.app.stream(initial_state):
        for key, value in event.items():
            print(f"\n--- Node: {key} ---")
            # print(value) # Verbose logging

if __name__ == "__main__":
    main()
