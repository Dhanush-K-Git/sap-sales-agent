# main.py — REPLACE entire file with this

import os
import asyncio
from dotenv import load_dotenv
from app.agents.supervisor_agent import run_supervisor

load_dotenv()

def main():
    print("\n" + "="*50)
    print("  SAP B1 Sales Team Agent")
    print("  Built for Techative Pvt Ltd Solutions")
    print("="*50)
    print("\nType 'exit' to quit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nGoodbye!")
            break
        if not user_input:
            continue
        try:
            response = asyncio.run(run_supervisor(user_input))
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    main()