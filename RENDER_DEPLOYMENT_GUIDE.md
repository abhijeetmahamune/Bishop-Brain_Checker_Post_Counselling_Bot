# Deployment Guide - Render.com

## Prerequisites
1. GitHub account with the repository pushed
2. Render.com account (free tier available)
3. OpenRouter API key (get from https://openrouter.ai/keys)

## Step-by-Step Deployment

### 1. Create a New Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"Connect your repository"** or paste the GitHub URL:
   ```
   https://github.com/abhijeetmahamune/Bishop-Brain_Checker_Post_Counselling_Bot.git
   ```
4. Click **"Connect"**

### 2. Configure the Service

**Service Settings:**
- **Name**: `brain-checker-api` (or your preferred name)
- **Runtime**: Python 3.11
- **Build Command**: (Auto-configured from render.yaml)
- **Start Command**: (Auto-configured from render.yaml)
- **Plan**: Free (for testing) or Paid for production

### 3. Add Environment Variables

Click **"Environment"** and add:

| Key | Value | Notes |
|-----|-------|-------|
| `OPENROUTER_API_KEY` | `sk-or-v1-xxxxx...` | Get from https://openrouter.ai/keys |
| `PYTHON_VERSION` | `3.11` | Already set in render.yaml |

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `backend/requirements.txt`
   - Start the server using the command in `render.yaml`
   - Provide a public URL (e.g., `https://brain-checker-api.onrender.com`)

### 5. Access Your Deployment

Once deployed:
- **Frontend**: https://brain-checker-api.onrender.com
- **API Docs**: https://brain-checker-api.onrender.com/docs
- **ReDoc**: https://brain-checker-api.onrender.com/redoc

## Troubleshooting

### Build Fails with "Preparing metadata (pyproject.toml): error"

**Solution:**
- Requirements.txt has pinned stable versions that have pre-built wheels
- File has been updated to use compatible versions
- Ensure `runtime.txt` contains: `python-3.11.7` or similar Python 3.11 version

### "Read-only file system" Error

**Solution:**
- This happens when packages try to compile Rust code
- Current requirements.txt uses stable versions with pre-built wheels
- If issue persists, try:
  ```
  pip install --no-cache-dir --no-build-isolation -r backend/requirements.txt
  ```

### Service Won't Start

**Check logs:**
1. Go to Render dashboard
2. Select your service
3. Click **"Logs"** tab
4. Look for error messages

**Common issues:**
- Missing `OPENROUTER_API_KEY` environment variable
- Wrong Python version specified
- Port already in use

### API Returns 502 Bad Gateway

**Solution:**
- Wait 1-2 minutes for service to fully start (Render takes time on free tier)
- Check logs for error messages
- Verify API key is valid at https://openrouter.ai/keys

## File Structure for Deployment

```
Bishop-Brain_Checker_Post_Counselling_Bot/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── pdf_utils.py           # PDF extraction
│   └── requirements.txt         # Python dependencies (PINNED VERSIONS)
├── index.html                  # Frontend UI
├── render.yaml                 # Render deployment config
├── runtime.txt                 # Python version specification
├── .env                        # Local env (NOT pushed to GitHub)
└── .gitignore                  # Git ignore rules
```

## Important Notes

1. **`.env` file**: Create locally, never commit to GitHub
   ```bash
   echo "OPENROUTER_API_KEY=sk-or-v1-xxxxx" > .env
   ```

2. **Requirements format**: Must have exact versions for Render:
   ```
   fastapi==0.104.1
   uvicorn==0.24.0
   pydantic==2.5.0
   # etc.
   ```

3. **Start command**: Uses `cd` to ensure correct working directory

4. **Free tier limitations**:
   - Service spins down after 15 minutes of inactivity
   - First request may take 30 seconds while service wakes up
   - Limited to 0.5 GB RAM
   - 100 GB/month bandwidth

## Updating After Deployment

To update your code:

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your message"
   git push origin main
   ```
3. Render automatically redeploys (if auto-deploy is enabled)

## Support

- **Render Support**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **OpenRouter Docs**: https://openrouter.ai/docs

---

**Last Updated**: April 15, 2026
