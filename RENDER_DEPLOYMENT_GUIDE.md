# Deployment Guide

## ⚠️ Known Issues with Render

### Issue 1: Pydantic-Core Rust Compilation
**Error**: `Read-only file system (os error 30)` during maturin build
**Solution**: ✅ Fixed - Using pydantic 1.10.15 with no Rust compilation

### Issue 2: Python Version Mismatch
**Error**: `pydantic.errors.ConfigError: unable to infer type for attribute` 
**Cause**: Render using Python 3.14 but pydantic 1.10 only supports up to 3.12
**Solution**: ✅ Fixed - Pinned to Python 3.11 in render.yaml and runtime.txt

---

## Option 1: Deploy on Render (With All Fixes)

### Prerequisites
1. GitHub account with latest code pushed
2. Render.com account (free tier available)
3. OpenRouter API key (get from https://openrouter.ai/keys)

### What's Fixed
- ✅ Python version pinned to 3.11 (in render.yaml and runtime.txt)
- ✅ Pydantic 1.10.15 (no Rust compilation)
- ✅ All packages have pre-built wheels
- ✅ FastAPI 0.95.2 (stable and compatible)

### Steps:

1. **Push latest code to GitHub:**
   ```bash
   git add .
   git commit -m "Fix Python version pinning and pydantic compatibility"
   git push origin main
   ```

2. **On Render Dashboard:**
   - Go to https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**
   - Connect GitHub repository: `Bishop-Brain_Checker_Post_Counselling_Bot`
   - **Settings:**
     - Name: `brain-checker-api`
     - Runtime: Auto-detected as Python 3.11
     - Build Command: Auto (from render.yaml)
     - Start Command: Auto (from render.yaml)
     - Plan: Free

3. **Add Environment Variable:**
   - Click **Environment**
   - Add: `OPENROUTER_API_KEY` = `sk-or-v1-xxxxx`

4. **Deploy:**
   - Click **Create Web Service**
   - Wait 3-5 minutes
   - Check logs to verify Python 3.11 is being used

### Verify Deployment
Once deployed, URLs will be:
```
https://brain-checker-api.onrender.com          (Frontend)
https://brain-checker-api.onrender.com/docs     (API Docs)
https://brain-checker-api.onrender.com/redoc    (ReDoc)
```

Check that logs show:
```
Python 3.11.x (not 3.14+)
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Option 2: Deploy on Railway (Recommended Alternative)

Railway automatically handles Python version management correctly.

### Quick Deploy

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   railway login
   railway init
   railway variables set OPENROUTER_API_KEY=sk-or-v1-xxxxx
   railway up
   ```

### Railway URL
```
https://<project-name>.railway.app
```

---

## Option 3: Deploy with Docker

Most reliable - fully avoids Python version conflicts.

### Docker File Already Provided
Use the `Dockerfile` in repository:

1. **On Render Dashboard:**
   - Create **Docker** service (not Web Service)
   - Connect GitHub repository
   - Render auto-detects Dockerfile
   
2. **Add environment variable:**
   - `OPENROUTER_API_KEY` = `sk-or-v1-xxxxx`

3. **Deploy and wait**

---

## Python Version Details

### Current Configuration
- **runtime.txt**: `python-3.11.7`
- **render.yaml**: `runtime: python-3.11`
- **Pydantic**: `1.10.15` (supports Python 3.11)
- **FastAPI**: `0.95.2` (stable with pydantic 1.10)

### Why 3.11?
- Pydantic 1.10 supports up to Python 3.12
- Render was using 3.14 by default, causing type inference errors
- Python 3.11 is stable, secure, and widely supported

### Upgrade Pydantic (Optional - Future)
To use pydantic 2.x (Python 3.12+):
```
# Only after Rusting compilation issue is resolved long-term
pydantic==2.5.0
fastapi==0.108.0
```

---

## Troubleshooting

### Build Fails: "unable to infer type for attribute 'name'"

**Cause**: Python 3.14+ being used with pydantic 1.10

**Solution**:
- Verify Render logs show "Python 3.11"
- If showing 3.14+, rebuild service:
  - Delete service on Render
  - Create new service
  - Ensure latest code is pushed to GitHub

### Build Fails: "Read-only file system"

**Cause**: Old pydantic trying to compile Rust

**Solution**: 
- Should be fixed with pydantic 1.10.15
- If persists, try Railway or Docker option

### Service Says "Running" but Returns 502

**Cause**: Service not fully started

**Solution**:
- Wait 1-2 minutes (cold start on free tier)
- Check logs for errors
-Try refreshing browser

### API Key Not Working

**Check**:
1. `OPENROUTER_API_KEY` is set in Render environment
2. Key is valid at https://openrouter.ai/keys
3. Key format: `sk-or-v1-xxxxx...`

---

## Files Structure

```
Bishop-Brain_Checker_Post_Counselling_Bot/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── pdf_utils.py              # PDF extraction
│   └── requirements.txt            # Python 3.11 compatible
├── runtime.txt                     # Python 3.11.7 pinned
├── render.yaml                     # Render deployment config
├── Dockerfile                      # Docker image (optional)
├── Procfile                       # Heroku/Railway config
├── index.html                     # Frontend
└── .env                          # Local only (never commit)
```

---

## Version Compatibility Matrix

| Component | Version | Python 3.11 | Notes |
|-----------|---------|-------------|-------|
| fastapi | 0.95.2 | ✅ | Stable, no issues |
| uvicorn | 0.22.0 | ✅ | Pairs with FastAPI |
| pydantic | 1.10.15 | ✅ | No Rust compilation |
| openai | 1.0.0 | ✅ | Pre-built wheels |
| pypdf | 3.17.0 | ✅ | Stable |
| pdfplumber | 0.9.0 | ✅ | Compatible |

---

## Deploy Checklist

Before deploying, verify:
- [ ] Latest code pushed to GitHub
- [ ] `runtime.txt` contains `python-3.11.7`
- [ ] `render.yaml` has `runtime: python-3.11`
- [ ] `backend/requirements.txt` updated with pydantic 1.10.15
- [ ] OpenRouter API key ready
- [ ] Selected correct deployment method

---

## Support

- **Python 3.11 Docs**: https://docs.python.org/3.11/
- **Pydantic 1.10 Docs**: https://docs.pydantic.dev/1.10/
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Render Support**: https://render.com/docs
- **Railway Support**: https://railway.app/docs

---

**Last Updated**: April 15, 2026

### Updated Requirements
We've updated `backend/requirements.txt` to use older, pre-built versions:
- `pydantic==1.10.13` (no Rust compilation needed)
- `fastapi==0.95.2` (compatible with pydantic 1.10)
- `openai==1.0.0` (stable, pre-built wheels)
- Other packages with guaranteed pre-built wheels

### Steps:

1. **Push latest code to GitHub:**
   ```bash
   git add .
   git commit -m "Fix Render deployment with stable versions"
   git push origin main
   ```

2. **On Render Dashboard:**
   - Go to https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select repository: `Bishop-Brain_Checker_Post_Counselling_Bot`
   - **Name**: `brain-checker-api`
   - **Runtime**: Python 3.11
   - **Build Command**: Leave default (uses render.yaml)
   - **Start Command**: Leave default (uses render.yaml)

3. **Add Environment Variable:**
   - Click **Environment**
   - Add: `OPENROUTER_API_KEY` = `sk-or-v1-xxxxx`

4. **Deploy:**
   - Click **Create Web Service**
   - Wait 2-5 minutes for deployment

### URLs After Deployment
```
https://brain-checker-api.onrender.com
https://brain-checker-api.onrender.com/docs
```

---

## Option 2: Deploy on Railway (Recommended Alternative)

Railway has better Python/Pydantic support and fewer compilation issues.

### Steps:

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize Railway Project:**
   ```bash
   railway init
   ```

4. **Add Environment Variable:**
   ```bash
   railway variables set OPENROUTER_API_KEY=sk-or-v1-xxxxx
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

### Railway URL
```
https://<project-name>.railway.app
```

---

## Option 3: Deploy with Docker (Most Reliable)

Docker avoids Python compilation issues entirely.

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy application
COPY . .

# Copy frontend files
COPY index.html .
COPY brain-checker-ai.html .

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "backend/main.py"]
```

### Step 2: Deploy on Docker-Based Platforms

**Option A: Deploy on Render with Docker**
1. Go to Render dashboard
2. Create Docker service instead of Web Service
3. Connect your repository
4. Render will auto-detect Dockerfile

**Option B: Deploy on Railway with Docker**
1. Railway auto-detects Dockerfile
2. Just run `railway up`

---

## Option 4: Deploy on Heroku (Legacy)

If you have a Heroku account:

### Create Procfile
```
web: python backend/main.py
```

### Deploy
```bash
heroku login
heroku create brain-checker-ai
git push heroku main
heroku config:set OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

---

## Troubleshooting

### "Read-only file system" Error on Render

**Cause:** Cargo/Rust trying to write to filesystem during pip install

**Solutions (in order):**
1. ✅ Use updated `requirements.txt` with older stable versions
2. Use Railway instead (better Python support)
3. Use Docker deployment
4. Use production plan instead of free (better resources)

### Dependencies Won't Install

**Check:**
```bash
# Locally verify requirements work
pip install -r backend/requirements.txt

# Test the app
python backend/main.py
```

### API Key Not Recognized

- Make sure `.env` is in project root
- Or set `OPENROUTER_API_KEY` in deployment platform environment variables
- Never commit `.env` to GitHub

### Service Won't Start

Check logs on deployment platform:
- **Render**: Logs tab in service dashboard
- **Railway**: CLI: `railway logs`
- **Heroku**: `heroku logs --tail`

Look for:
- Missing imports
- API key errors
- Port binding issues

---

## Version Compatibility

Current working versions:
| Package | Version | Notes |
|---------|---------|-------|
| fastapi | 0.95.2 | Stable, no Rust compilation |
| uvicorn | 0.22.0 | Pairs well with FastAPI 0.95 |
| pydantic | 1.10.13 | No pydantic-core dependency |
| openai | 1.0.0 | Pre-built wheels available |
| pypdf | 3.17.0 | Stable PDF processing |
| pdfplumber | 0.9.0 | Reliable PDF extraction |

---

## Local Development

To test locally before deploying:

```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file
echo OPENROUTER_API_KEY=sk-or-v1-xxxxx > .env

# Run server
python backend/main.py

# Open browser
# http://localhost:8000
```

---

## Next Steps

1. **Try one of the deployment options above**
2. **Monitor deployment logs** for errors
3. **Test upload feature** when deployed
4. **Set up auto-deploy** from GitHub
5. **Monitor costs** (some platforms may charge after free tier expires)

---

## Support

- **Render Issues**: https://render.com/docs
- **Railway Issues**: https://railway.app/docs
- **Docker Issues**: https://docs.docker.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **OpenRouter API**: https://openrouter.ai/docs

---

**Last Updated**: April 15, 2026

