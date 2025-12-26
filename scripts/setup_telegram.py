#!/usr/bin/env python3
"""Quick Telegram setup script."""

import sys
import getpass
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("=" * 60)
    print("  Telegram Bot Setup")
    print("=" * 60)
    print()

    print("Step 1: Create a Telegram Bot")
    print("  1. Open Telegram and search for @BotFather")
    print("  2. Send: /newbot")
    print("  3. Follow instructions to create your bot")
    print("  4. Copy the bot token (looks like: 123456:ABC-DEF...)")
    print()

    bot_token = getpass.getpass("Enter your Telegram Bot Token: ")

    if not bot_token:
        print("\n❌ No token provided")
        return

    # Store bot token
    print("\n📝 Storing bot token...")

    try:
        from pulsepilot.core.secrets import get_secrets_manager

        sm = get_secrets_manager()
        sm.set_secret("TELEGRAM_BOT_TOKEN", bot_token)
        print("✅ Bot token stored")

    except Exception as e:
        print(f"❌ Error storing token: {e}")
        return

    # Get chat ID
    print("\nStep 2: Get Your Chat ID")
    print("  1. Send a message to your bot in Telegram")
    print("  2. Press Enter here to fetch your chat ID")
    input("\nPress Enter after sending a message to your bot...")

    try:
        from pulsepilot.tools.telegram_get_chat_id import main as get_chat_id

        # This will show chat IDs
        print("\nFetching chat IDs...")
        get_chat_id()

        print()
        chat_id = input("Enter the Chat ID you want to use: ")

        if chat_id:
            sm.set_secret("TELEGRAM_CHAT_ID", chat_id)
            print("✅ Chat ID stored")

    except Exception as e:
        print(f"⚠️  Could not auto-fetch chat ID: {e}")
        print("\nManual method:")
        print(f"  1. Visit: https://api.telegram.org/bot{bot_token}/getUpdates")
        print("  2. Find your chat ID in the JSON response")

        chat_id = input("\nEnter Chat ID manually (or press Enter to skip): ")
        if chat_id:
            sm.set_secret("TELEGRAM_CHAT_ID", chat_id)
            print("✅ Chat ID stored")

    # Test the setup
    if chat_id:
        print("\n🧪 Testing Telegram bot...")

        try:
            from pulsepilot.agents.deployment import DeploymentAgent
            from pulsepilot.core.memory import SharedMemory

            agent = DeploymentAgent(memory=SharedMemory())
            result = agent.push_to_telegram("🎉 Hello from PulsePilot! Setup successful!")

            if result['status'] == 'sent':
                print(f"\n✅ Test message sent! Check your Telegram!")
                print(f"   Message ID: {result['id']}")
            else:
                print(f"\n⚠️  Test result: {result['status']}")
                print(f"   Reason: {result.get('reason', 'unknown')}")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")

    # Update .env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'a') as f:
            f.write("\n# Telegram Configuration\n")
            f.write("DEPLOYMENT_CHANNELS=telegram\n")
        print("\n✅ Updated .env with Telegram channel")

    print("\n" + "=" * 60)
    print("  Telegram Setup Complete! 🎉")
    print("=" * 60)
    print("\nYou can now:")
    print("  - Send messages to Telegram")
    print("  - Use the deployment agent")
    print("  - Run campaigns with Telegram output")
    print("\nNext: Add more platforms or start posting!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
