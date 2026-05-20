# X (Twitter) Integration via xurl

Hermes connects to X through the `xurl` CLI — posting, reading timeline, searching, and DMs.

---

## Prerequisites

1. Free X Developer account: https://developer.x.com/en/portal/dashboard
2. Create a **Project** → then an **App** within it
3. App permissions: **Read and Write** (not Read-only)
4. App type: **Web App, Automated App or Bot**
5. Callback URL: `http://localhost:8080/callback` (exact match, no trailing slash)
6. Website URL: `https://x.com/<your_username>` (profile URL is sufficient)

---

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/xdevplatform/xurl/main/install.sh | bash
```

---

## Authentication Flow

### Step 1: Register app with xurl

Get **Client ID** and **Client Secret** from Developer Portal → App → Keys and tokens:

```bash
xurl auth apps add my-app --client-id <CLIENT_ID> --client-secret <CLIENT_SECRET>
```

### Step 2: OAuth 2.0 Authorization Code Flow

Must run on a machine **with a browser** (localhost redirect):

```bash
xurl auth oauth2 --app my-app <X_USERNAME>
```

This opens the browser → you log into X → grant permissions → redirects to localhost → token stored.

### Verify

```bash
xurl --app my-app whoami
```

---

## Tier Limits

| Tier | Price | Post Tweets | Read |
|------|-------|------------|------|
| **Free** | $0 | ❌ No credits for POST | ✅ |
| **Basic** | $100/mo | ✅ 3,000 posts/mo | ✅ |
| **Pro** | $5,000/mo | ✅ Unlimited | ✅ |

**Free tier gotcha:** OAuth2 authentication works fine, `whoami` and `timeline` work, but any POST action (tweet, reply, quote) returns `CreditsDepleted`. You must upgrade to Basic for write access.

---

## Common Pitfalls

### "Cannot authorize app" / "Không thể cấp quyền"

This happens when the app is in **Development** mode and your account isn't a test user:

1. Developer Portal → App Settings → **User authentication settings**
2. Scroll to **Test users** at the bottom
3. Add `@yourusername`
4. Save and wait 2-3 minutes for propagation

### 401 on OAuth 1.0a

X Free tier may not support OAuth 1.0a for user-context endpoints. Use OAuth 2.0 (authorization code flow) instead.

### 403 on client credentials grant

Client credentials (`grant_type=client_credentials`) requires elevated app permissions not available on Free tier.

### Callback URL mismatch

The callback URL in Developer Portal must be **exactly** `http://localhost:8080/callback`:
- No `https`
- No trailing `/`
- No other port
- Must match xurl's built-in default

---

## Useful Commands

```bash
xurl --app my-app whoami              # Verify auth
xurl --app my-app timeline            # Home timeline
xurl --app my-app search "query" -n 10  # Search X
xurl --app my-app user @handle        # Look up user
xurl --app my-app post "text"         # Post tweet (needs Basic tier)
xurl --app my-app reply <id> "text"   # Reply (needs Basic tier)
xurl --app my-app quote <id> "text"   # Quote tweet (needs Basic tier)
```

---

## Alternative Data Source: thefeed.today

When X API credits are exhausted (Free tier), `thefeed.today` provides a browser-based alternative:

- No auth required
- No rate limits
- Pre-summarized tweets with category filters (Crypto, Tech, etc.)
- Accessible via Hermes browser tools

See `ai-labs/resource/skills/x-news-brief/` for the briefing skill built on this source.
