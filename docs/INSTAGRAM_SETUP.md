# Instagram Setup Guide for PulsePilot

Complete guide to connecting your Instagram account for posting via API.

## 📋 Overview

Instagram requires:
- ✅ Instagram Business or Creator Account
- ✅ Connected Facebook Page
- ✅ Facebook App with Instagram API access
- ✅ Long-lived access token (60 days, auto-refreshes)

**Time required:** 15-20 minutes (first time)

---

## 🚀 Quick Start (Interactive)

Run the setup script - it guides you through everything:

```bash
python scripts/setup_instagram.py
```

This will walk you through each step and test your connection.

---

## 📝 Manual Setup Instructions

### Step 1: Convert to Instagram Business Account

Instagram API only works with Business or Creator accounts.

**On your phone:**

1. Open Instagram app
2. Go to **Settings** → **Account**
3. Tap **"Switch to Professional Account"**
4. Choose **"Business"** or **"Creator"**
5. **Connect to a Facebook Page** (required!)
   - Create a new Facebook Page if needed
   - Can be any name (e.g., "My Business Page")

⚠️ **Important:** You MUST connect to a Facebook Page to use the API!

**Verify:**
- Profile shows "Business" or "Creator" under your name
- Settings has "Business" or "Creator tools" section

---

### Step 2: Create Facebook App

1. **Go to:** https://developers.facebook.com/apps

2. **Create App:**
   - Click **"Create App"**
   - Choose **"Business"** as app type
   - App Name: `PulsePilot` (or any name)
   - Contact Email: Your email
   - Click **"Create App"**

3. **Add Instagram Product:**
   - In app dashboard, click **"Add Product"**
   - Find **"Instagram"** → Click **"Set Up"**
   - Also add **"Instagram Basic Display"**

4. **Configure App:**
   - Go to **Settings** → **Basic**
   - Note your **App ID** and **App Secret**

---

### Step 3: Get Your Instagram Business Account ID

**Using Graph API Explorer:**

1. Go to: https://developers.facebook.com/tools/explorer/

2. **Get Page ID:**
   - Select your app from dropdown
   - Click **"Generate Access Token"**
   - Grant permissions
   - Query: `me/accounts`
   - Copy your Facebook Page ID from response

3. **Get Instagram Business Account ID:**
   - Query: `{PAGE_ID}?fields=instagram_business_account`
   - Copy the `instagram_business_account.id` value
   - This is your **Instagram Business Account ID** (save it!)

**Example response:**
```json
{
  "instagram_business_account": {
    "id": "17841405793187218"  ← This is what you need!
  },
  "id": "107..."
}
```

---

### Step 4: Get Long-Lived Access Token

You need a token that lasts 60 days (auto-refreshes with PulsePilot).

#### Option A: Graph API Explorer (Easiest)

1. Go to: https://developers.facebook.com/tools/explorer/

2. **Generate token:**
   - Select your app
   - Click **"Generate Access Token"**

3. **Select permissions:**
   - ✓ `instagram_basic`
   - ✓ `instagram_content_publish`
   - ✓ `pages_show_list`
   - ✓ `pages_read_engagement`

4. **Authorize** and copy the token

5. **Convert to long-lived token:**

   In Graph API Explorer, run this query:
   ```
   oauth/access_token?grant_type=fb_exchange_token&client_id={YOUR_APP_ID}&client_secret={YOUR_APP_SECRET}&fb_exchange_token={YOUR_SHORT_TOKEN}
   ```

   Replace:
   - `{YOUR_APP_ID}` - From app dashboard
   - `{YOUR_APP_SECRET}` - From app dashboard → Settings → Basic
   - `{YOUR_SHORT_TOKEN}` - Token you just generated

6. **Copy the long-lived token** from the response

#### Option B: Using cURL

```bash
curl -X GET "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={YOUR_APP_ID}&client_secret={YOUR_APP_SECRET}&fb_exchange_token={YOUR_SHORT_TOKEN}"
```

Response:
```json
{
  "access_token": "EAAGm0PX4ZCpsBO...",  ← Long-lived token (60 days)
  "token_type": "bearer",
  "expires_in": 5183944
}
```

---

### Step 5: Store Credentials in PulsePilot

#### Using the CLI:

```bash
# Store Instagram User ID
python -m pulsepilot.cli_secrets set INSTAGRAM_IG_USER_ID --value="17841405793187218"

# Store OAuth token
python -m pulsepilot.cli_secrets oauth-set instagram \
    --access-token="YOUR_LONG_LIVED_TOKEN" \
    --expires-in=5184000
```

#### Using Python:

```python
from pulsepilot.core.secrets import get_secrets_manager
from pulsepilot.core.oauth import InstagramOAuthManager, OAuthToken

sm = get_secrets_manager()

# Store Instagram Business Account ID
sm.set_secret("INSTAGRAM_IG_USER_ID", "17841405793187218")

# Create OAuth manager
instagram = InstagramOAuthManager(sm)

# Create and store token
token = OAuthToken(
    access_token="YOUR_LONG_LIVED_TOKEN",
    refresh_token="YOUR_LONG_LIVED_TOKEN",  # Same for Instagram
    expires_in=5184000,  # 60 days
    token_type="Bearer"
)

instagram.set_token(token)
print("✅ Instagram configured!")
```

---

### Step 6: Enable Instagram Channel

Update your `.env`:

```bash
echo "DEPLOYMENT_CHANNELS=instagram" >> .env
# Or add to existing channels: telegram,instagram,facebook
```

---

### Step 7: Test Your Setup

```python
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.memory import SharedMemory

agent = DeploymentAgent(memory=SharedMemory())

# Test posting (requires publicly accessible image)
result = agent.push_to_instagram(
    caption="Test post from PulsePilot! 🚀",
    image_url="https://picsum.photos/1080/1080"  # Example image
)

if result['status'] == 'sent':
    print(f"✅ Posted! Instagram Media ID: {result['id']}")
else:
    print(f"❌ Failed: {result.get('error')}")
```

---

## 🔄 Token Auto-Refresh

PulsePilot automatically refreshes your Instagram token before it expires (5 minutes before the 60-day expiration).

**How it works:**
1. Before each post, checks if token expires soon
2. If < 5 minutes remaining, automatically refreshes
3. Stores new token in secrets manager
4. No action needed from you!

**To manually refresh:**
```bash
python -m pulsepilot.cli_secrets oauth-refresh instagram
```

---

## 📸 Instagram Posting Requirements

Instagram has specific requirements:

### ✅ Image Requirements:
- **Format:** JPG or PNG
- **Size:** Min 320px, recommended 1080x1080 (square)
- **Aspect ratio:** 1.91:1 to 4:5 (landscape to portrait)
- **File size:** Max 8 MB
- **Location:** Must be publicly accessible URL

### ✅ Caption Requirements:
- Max 2,200 characters
- Up to 30 hashtags
- Mentions with @ symbol

### ✅ Rate Limits:
- ~25 posts per day per account
- 200 API calls per hour per app

### ❌ Not Supported:
- Text-only posts (image required)
- Videos (use Instagram Graph API separately)
- Stories (different endpoint)
- Reels (different endpoint)

---

## 🧪 Testing Examples

### Test with Sample Image:

```python
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.memory import SharedMemory

agent = DeploymentAgent(memory=SharedMemory())

# Use a test image service
result = agent.push_to_instagram(
    caption="Testing PulsePilot Instagram integration! 🚀 #test #automation",
    image_url="https://picsum.photos/1080/1080"
)

print(result)
```

### Test with Your Own Image:

```python
# Upload image to your hosting (AWS S3, Imgur, etc.)
# Make sure URL is publicly accessible

result = agent.push_to_instagram(
    caption="My awesome post! #marketing #socialmedia",
    image_url="https://your-bucket.s3.amazonaws.com/image.jpg"
)
```

---

## 🔧 Troubleshooting

### "Invalid access token"

**Cause:** Token expired or invalid

**Fix:**
1. Generate new long-lived token (Step 4)
2. Update stored token:
   ```bash
   python -m pulsepilot.cli_secrets oauth-set instagram --access-token="NEW_TOKEN"
   ```

### "User does not have permission"

**Cause:** Missing Instagram API permissions

**Fix:**
1. Go to Graph API Explorer
2. Generate new token with these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`

### "Invalid Instagram user"

**Cause:** Wrong Instagram Business Account ID

**Fix:**
1. Verify your ID: https://developers.facebook.com/tools/explorer/
2. Query: `me/accounts` then `{PAGE_ID}?fields=instagram_business_account`
3. Update:
   ```bash
   python -m pulsepilot.cli_secrets set INSTAGRAM_IG_USER_ID --value="CORRECT_ID"
   ```

### "Image URL is not accessible"

**Cause:** Image URL is not publicly accessible

**Fix:**
- Use public image hosting (Imgur, AWS S3 with public access, etc.)
- Verify URL works in browser incognito mode
- Check URL is HTTPS (not HTTP)

### "Rate limit exceeded"

**Cause:** Too many posts in short time

**Fix:**
- Instagram limits ~25 posts per day
- Wait a few hours before posting again
- Spread posts throughout the day

---

## 📊 Check Your Setup

Verify everything is configured:

```bash
# Check Instagram User ID
python -m pulsepilot.cli_secrets get INSTAGRAM_IG_USER_ID

# Check OAuth token status
python -m pulsepilot.cli_secrets oauth-get instagram

# Test API connection
python scripts/setup_instagram.py  # Re-run to test
```

---

## 🔐 Security Notes

✅ **Access token is encrypted** at rest (cloud providers)
✅ **Auto-refreshes** before expiration
✅ **Limited scope** - only posting permissions
✅ **Audit logging** available (cloud providers)

**Never:**
- ❌ Share your access token
- ❌ Commit tokens to Git
- ❌ Use personal account tokens in production

---

## 📚 Additional Resources

- **Facebook Graph API Docs:** https://developers.facebook.com/docs/graph-api
- **Instagram Graph API:** https://developers.facebook.com/docs/instagram-api
- **Content Publishing:** https://developers.facebook.com/docs/instagram-api/guides/content-publishing
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer/

---

## ✅ Quick Checklist

Before posting to Instagram:

- [ ] Instagram Business/Creator account set up
- [ ] Connected to Facebook Page
- [ ] Facebook App created
- [ ] Instagram API added to app
- [ ] Long-lived access token generated
- [ ] Instagram Business Account ID obtained
- [ ] Credentials stored in PulsePilot
- [ ] Instagram channel enabled in `.env`
- [ ] Test post successful

---

## 🆘 Need Help?

**Still having issues?**

1. Re-run setup script: `python scripts/setup_instagram.py`
2. Check permissions in Graph API Explorer
3. Verify account is Business type (not Personal)
4. Check Facebook Page is connected
5. Review error messages in deployment agent

**For more help:**
- See `docs/SECURITY.md` - OAuth setup section
- See `docs/QUICKSTART_SECURITY.md` - Quick reference
- Check Instagram API status: https://developers.facebook.com/status

---

## 🎉 You're Ready!

Once setup is complete, you can post to Instagram from your campaigns:

```python
from pulsepilot.agents.deployment import DeploymentAgent
from pulsepilot.core.memory import SharedMemory

agent = DeploymentAgent(memory=SharedMemory())
result = agent.push_to_instagram(
    caption="Automated post from PulsePilot! 🚀",
    image_url="https://example.com/image.jpg"
)
```

OAuth tokens auto-refresh, so you're good for months!
