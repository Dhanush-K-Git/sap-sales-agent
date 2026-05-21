import os
from anthropic import Anthropic
from dotenv import load_dotenv

# 1. Load the environment variables from your .env file
load_dotenv()

# 2. Grab the key
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ ERROR: 'ANTHROPIC_API_KEY' was not found in your .env file.")
else:
    print(f"Attempting connection with key starting with: {api_key[:12]}...")
    
    try:
        # 3. Initialize the client
        client = Anthropic(api_key=api_key)
        
        # 4. Make a tiny request to Claude Opus 4.7
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=20,
            messages=[{"role": "user", "content": "Connection check: Say 'Ready to work!'"}]
        )
        
        print(f"✅ SUCCESS! Claude responded: {response.content[0].text}")

    except Exception as e:
        print(f"❌ API TEST FAILED!")
        print(f"Error Details: {e}")