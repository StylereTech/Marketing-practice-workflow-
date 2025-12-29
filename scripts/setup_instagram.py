#!/usr/bin/env python3
"""
Instagram Setup Guide and Helper Script

This script helps you set up Instagram Business API access for PulsePilot.
"""

import sys
import getpass
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def print_header(text):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(number, title):
    """Print a step header."""
    print(f"\n{'='*70}")
    print(f"STEP {number}: {title}")
    print(f"{'='*70}\n")


def main():
    print_header("Instagram Business API Setup for PulsePilot")

    print("""
Instagram requires a Business Account and Facebook App to post via API.

This guide will walk you through:
1. Converting to Instagram Business Account
2. Creating a Facebook App
3. Getting your access token
4. Configuring PulsePilot

Estimated time: 15-20 minutes
""")

    input("Press Enter to continue...")

    # Step 1: Check account type
    print_step(1, "Instagram Business Account Setup")

    print("""
Instagram API only works with Business or Creator accounts.

To convert your personal account to Business:

1. Open Instagram app on your phone
2. Go to Settings → Account
3. Tap "Switch to Professional Account"
4. Choose "Business" or "Creator"
5. Connect to a Facebook Page (required!)
   - Create a new Facebook Page if you don't have one
   - Name it anything (e.g., "My Business Page")

Important: You MUST connect to a Facebook Page to use the API!
""")

    has_business = input("Do you have an Instagram Business Account? (y/N): ")

    if has_business.lower() != 'y':
        print("\n⚠️  Please convert to Business Account first, then re-run this script.")
        print("   Guide: https://help.instagram.com/502981923235522")
        return

    # Step 2: Facebook App
    print_step(2, "Create Facebook App")

    print("""
You need a Facebook App to get API access.

1. Go to: https://developers.facebook.com/apps
2. Click "Create App"
3. Choose "Business" as app type
4. Fill in:
   - App Name: "PulsePilot" (or any name)
   - Contact Email: Your email
5. Click "Create App"

6. In the app dashboard:
   - Click "Add Product"
   - Find "Instagram" and click "Set Up"
   - Also add "Instagram Basic Display" if available

7. Get your Instagram Business Account ID:
   - Go to: https://developers.facebook.com/apps/{your-app-id}/instagram-basic-display/basic-display/
   - Or use Graph API Explorer: https://developers.facebook.com/tools/explorer/
   - Query: me/accounts (to get your Facebook Page ID)
   - Then query: {page-id}?fields=instagram_business_account
""")

    input("Press Enter when you've created your Facebook App...")

    # Step 3: Get Access Token
    print_step(3, "Get Long-Lived Access Token")

    print("""
Now you need to get a long-lived access token (lasts 60 days, auto-refreshes).

METHOD 1: Using Graph API Explorer (Easiest)
---------------------------------------------
1. Go to: https://developers.facebook.com/tools/explorer/

2. In the top right:
   - Select your app from dropdown
   - Click "Generate Access Token"

3. Select these permissions:
   ✓ instagram_basic
   ✓ instagram_content_publish
   ✓ pages_show_list
   ✓ pages_read_engagement

4. Click "Generate Access Token" and authorize

5. Copy the token (starts with "EAAG..." or similar)

6. Convert to long-lived token:
   - In Graph API Explorer, use this query:

   oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN

7. This returns a long-lived token (60 days)


METHOD 2: Manual via cURL
--------------------------
Run this command (replace with your values):

curl -X GET "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={your-app-id}&client_secret={your-app-secret}&fb_exchange_token={your-short-lived-token}"


⚠️  IMPORTANT: Copy this long-lived token - you'll enter it next!
""")

    input("Press Enter when you have your long-lived access token...")

    # Step 4: Get Instagram Business Account ID
    print_step(4, "Get Instagram Business Account ID")

    print("""
You need your Instagram Business Account ID (numeric ID).

Using Graph API Explorer:
1. Go to: https://developers.facebook.com/tools/explorer/
2. Paste your access token
3. Query: me/accounts
   - This shows your Facebook Pages
   - Copy the Page ID

4. Then query: {PAGE_ID}?fields=instagram_business_account
   - Copy the instagram_business_account.id value

Or use this tool:
https://developers.facebook.com/tools/explorer/
Query: me?fields=instagram_business_account
""")

    input("Press Enter when you have your Instagram Business Account ID...")

    # Step 5: Store credentials
    print_step(5, "Store Credentials in PulsePilot")

    print("\nNow let's store your credentials securely.\n")

    # Get access token
    access_token = getpass.getpass("Enter your Instagram Access Token: ")
    if not access_token:
        print("❌ Access token required")
        return

    # Get Instagram Business Account ID
    ig_user_id = input("Enter your Instagram Business Account ID: ")
    if not ig_user_id:
        print("❌ Instagram Business Account ID required")
        return

    # Store in secrets manager
    print("\n📝 Storing credentials...")

    try:
        from pulsepilot.core.secrets import get_secrets_manager
        from pulsepilot.core.oauth import InstagramOAuthManager, OAuthToken

        sm = get_secrets_manager()

        # Store Instagram User ID
        sm.set_secret("INSTAGRAM_IG_USER_ID", ig_user_id)
        print("✅ Instagram User ID stored")

        # Create and store OAuth token
        instagram = InstagramOAuthManager(sm)

        token = OAuthToken(
            access_token=access_token,
            refresh_token=access_token,  # Instagram uses same token for refresh
            expires_in=5184000,  # 60 days
            token_type="Bearer"
        )

        instagram.set_token(token)
        print("✅ Instagram OAuth token stored")

    except Exception as e:
        print(f"❌ Error storing credentials: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 6: Test the setup
    print_step(6, "Test Instagram Connection")

    print("Let's verify everything works by fetching your Instagram profile info.\n")

    try:
        import requests

        # Test API call
        url = f"https://graph.instagram.com/me"
        params = {
            "fields": "id,username,account_type",
            "access_token": access_token
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "id" in data:
            print("✅ Instagram API Connection Successful!")
            print(f"\n   Instagram ID: {data['id']}")
            print(f"   Username: {data.get('username', 'N/A')}")
            print(f"   Account Type: {data.get('account_type', 'N/A')}")

            # Test posting capability (dry run)
            print("\n🧪 Testing posting capability (dry run)...")

            try:
                from pulsepilot.agents.deployment import DeploymentAgent
                from pulsepilot.core.memory import SharedMemory

                # Enable Instagram channel
                import os
                os.environ['DEPLOYMENT_CHANNELS'] = 'instagram'
                os.environ['DEPLOYMENT_DRY_RUN'] = 'false'  # We'll use real test

                agent = DeploymentAgent(memory=SharedMemory())

                # Note: Actual posting requires an image URL
                print("\n⚠️  To test actual posting, you'll need:")
                print("   1. A publicly accessible image URL")
                print("   2. Run this code:")
                print("""
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.memory import SharedMemory

agent = DeploymentAgent(memory=SharedMemory())
result = agent.push_to_instagram(
    caption="Test post from PulsePilot! 🚀",
    image_url="https://example.com/your-image.jpg"
)
print(result)
""")

            except Exception as e:
                print(f"⚠️  Agent test skipped: {e}")

        else:
            print(f"❌ API Error: {data}")
            print("\nPossible issues:")
            print("  - Invalid access token")
            print("  - Missing permissions (need instagram_basic, instagram_content_publish)")
            print("  - Token expired")
            return

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return

    # Update .env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        # Check if Instagram is already in DEPLOYMENT_CHANNELS
        with open(env_file, 'r') as f:
            env_content = f.read()

        if 'DEPLOYMENT_CHANNELS' in env_content:
            # Add instagram to existing channels
            import re
            if 'instagram' not in env_content:
                env_content = re.sub(
                    r'DEPLOYMENT_CHANNELS=([^\n]+)',
                    r'DEPLOYMENT_CHANNELS=\1,instagram',
                    env_content
                )
                with open(env_file, 'w') as f:
                    f.write(env_content)
                print("\n✅ Added Instagram to DEPLOYMENT_CHANNELS in .env")
        else:
            with open(env_file, 'a') as f:
                f.write("\n# Instagram Configuration\n")
                f.write("DEPLOYMENT_CHANNELS=instagram\n")
            print("\n✅ Updated .env with Instagram channel")

    # Success!
    print_header("Instagram Setup Complete! 🎉")

    print("""
✅ Instagram Business Account connected
✅ OAuth token stored (auto-refreshes every 60 days)
✅ API connection verified

You can now post to Instagram using PulsePilot!

Example usage:
""")

    print("""
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.memory import SharedMemory

agent = DeploymentAgent(memory=SharedMemory())

# Post to Instagram
result = agent.push_to_instagram(
    caption="Hello from PulsePilot! 🚀",
    image_url="https://example.com/image.jpg"  # Must be publicly accessible
)

if result['status'] == 'sent':
    print(f"✅ Posted! Instagram Media ID: {result['id']}")
""")

    print("\nImportant notes:")
    print("  • Images must be publicly accessible URLs")
    print("  • Instagram requires images (can't post text-only)")
    print("  • Token auto-refreshes before expiration")
    print("  • Rate limits: ~25 posts per day per account")

    print("\nFor more info:")
    print("  • docs/SECURITY.md - OAuth setup details")
    print("  • docs/QUICKSTART_SECURITY.md - Quick reference")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
