#!/usr/bin/env python3
"""Quick OpenAI setup and test script."""

import sys
import getpass
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("=" * 60)
    print("  OpenAI API Key Setup")
    print("=" * 60)
    print()
    
    # Get API key
    print("Enter your OpenAI API key (starts with 'sk-')")
    print("Get one from: https://platform.openai.com/api-keys")
    print()
    api_key = getpass.getpass("OpenAI API Key: ")
    
    if not api_key:
        print("\n❌ No API key provided")
        return
    
    if not api_key.startswith('sk-'):
        print("\n⚠️  Warning: OpenAI keys usually start with 'sk-'")
        confirm = input("Continue anyway? (y/N): ")
        if confirm.lower() != 'y':
            return
    
    # Store in secrets manager
    print("\n📝 Storing API key...")
    
    try:
        from pulsepilot.core.secrets import get_secrets_manager
        
        sm = get_secrets_manager()
        success = sm.set_secret("OPENAI_API_KEY", api_key)
        
        if success:
            print("✅ API key stored successfully!")
        else:
            print("❌ Failed to store API key")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test the API key
    print("\n🧪 Testing API key...")
    
    try:
        from pulsepilot.core.llm import LLMInterface
        
        llm = LLMInterface(provider="openai")
        
        print("   Sending test request to OpenAI...")
        response = llm.generate(
            system_prompt="You are a helpful assistant. Respond in one short sentence.",
            user_prompt="Say hello and confirm you're working!",
            temperature=0.7
        )
        
        print(f"\n✅ OpenAI API is working!")
        print(f"   Response: {response}\n")
        
        # Check .env configuration
        env_file = Path(__file__).parent / ".env"
        if not env_file.exists():
            print("📝 Creating .env configuration file...")
            with open(env_file, 'w') as f:
                f.write("# PulsePilot Configuration\n")
                f.write("SECRETS_PROVIDER=env\n\n")
                f.write("# Model Configuration\n")
                f.write("ORCHESTRATOR_MODEL=gpt-4-turbo-preview\n")
                f.write("AGENT_MODEL=gpt-4-turbo-preview\n\n")
                f.write("# System Configuration\n")
                f.write("ENVIRONMENT=development\n")
                f.write("LOG_LEVEL=INFO\n")
                f.write("DEPLOYMENT_DRY_RUN=true\n")
            print("✅ Created .env file\n")
        
        print("=" * 60)
        print("  Setup Complete! 🎉")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. ✅ OpenAI configured and tested")
        print("  2. 📱 Configure social media platforms (optional)")
        print("  3. 🚀 Start creating and posting content!")
        print("\nTo configure Telegram (easiest platform):")
        print("  python scripts/setup_telegram.py")
        print("\nTo test content generation:")
        print("  python examples/simple_example.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nPossible issues:")
        print("  - Invalid API key")
        print("  - No credits/quota remaining")
        print("  - Network connectivity issue")
        print("\nCheck your key at: https://platform.openai.com/api-keys")
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
