import os
from dotenv import load_dotenv
from agents.supervisor_agent import run_supervisor

load_dotenv()

# ─────────────────────────────────────────────
# 🎯 MAIN ENTRY POINT
# ─────────────────────────────────────────────

def main():
    print("\n" + "="*50)
    print("  SAP B1 Sales Team Agent")
    print("  Built for Techative Pvt Ltd Solutions")
    print("="*50)
    print("\nType 'exit' to quit\n")

    while True:
        # Get user input
        user_input = input("You: ").strip()

        # Exit condition
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nGoodbye! 👋")
            break

        # Skip empty messages
        if not user_input:
            continue

        try:
            # Send to supervisor and get response
            response = run_supervisor(user_input)
            print(f"\nAgent: {response}\n")

        except Exception as e:
            print(f"\nError: {str(e)}\n")
            print("Please try again!\n")


if __name__ == "__main__":
    main()