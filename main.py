import os
from langchain_groq import ChatGroq

llm = ChatGroq(
    temperature=0, 
    groq_api_key=os.getenv("GROQ_API_KEY"), 
    model_name="llama-3.3-70b-versatile" # or "llama3-8b-8192"
)

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
            print("\nGoodbye! 👋")
            break

        if not user_input:
            continue

        try:
            response = run_supervisor(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"\nError: {str(e)}\n")
            print("Please try again!\n")


if __name__ == "__main__":
    main()