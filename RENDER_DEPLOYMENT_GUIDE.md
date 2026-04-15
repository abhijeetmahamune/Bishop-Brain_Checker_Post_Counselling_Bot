# Deployment Guide

## ⚠️ Known Issues with Render

Render.com has issues with `pydantic-core` compilation on their free tier. If you encounter the error:
```
error: failed to create directory `/usr/local/cargo/registry/cache/...`
Read-only file system (os error 30)
```

**Solution**: Use the **Fixed Requirements** and try the alternative deployment methods below.

---

## Option 1: Deploy on Render (With Fixed Requirements)

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

