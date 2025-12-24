import os
import sys
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env or environment.")
        print("Please create a .env file and add: TELEGRAM_BOT_TOKEN=your_token_here")
        sys.exit(1)
        
    print(f"Checking for updates for bot token: {token[:10]}...")
    print("💡 Instruction: Send a message to your bot first, then run this tool.")
    
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get("ok"):
            print(f"❌ Telegram API Error: {data.get('description')}")
            sys.exit(1)
            
        results = data.get("result", [])
        if not results:
            print("📭 No messages found. Send a message to the bot and try again.")
            sys.exit(0)
            
        print("\n--- Recent Chat IDs ---")
        seen_chats = set()
        for update in reversed(results):
            message = update.get("message")
            if not message:
                continue
            
            chat = message.get("chat")
            chat_id = chat.get("id")
            username = chat.get("username", "No Username")
            first_name = chat.get("first_name", "")
            
            if chat_id not in seen_chats:
                print(f"ID: {chat_id} | Name: {first_name} (@{username})")
                seen_chats.add(chat_id)
        
        print("\nCopy the ID you want and add it to your .env as: TELEGRAM_CHAT_ID=xxxx")
                
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
