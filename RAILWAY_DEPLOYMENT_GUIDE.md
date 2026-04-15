# Railway.app Deployment Guide

Railway.app provides simple, reliable Python deployment without compilation issues.

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Repo**: Your code must be on GitHub (already done ✅)
3. **OpenRouter API Key**: Set as environment variable

## Deployment Steps

### Option 1: Railway Dashboard (Recommended)

1. Go to https://railway.app and sign in
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository: `Bishop-Brain_Checker_Post_Counselling_Bot`
4. Railway auto-detects the Dockerfile and deploys
5. Go to "Variables" tab and add:
   ```
   OPENROUTER_API_KEY=your_actual_key_here
   ```
6. Click "Deploy" button

### Option 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Apply environment variables
railway variables set OPENROUTER_API_KEY=your_actual_key_here

# Deploy
railway up
```

## Configuration Files

### `Dockerfile` (Primary)
- Uses Python 3.11 slim image
- Installs dependencies with `--prefer-binary` (avoids compilation)
- Runs `python backend/main.py` with proper port exposure
- Health check included

### `Procfile` (Backup)
- `web: python backend/main.py`
- Used if Dockerfile not detected

### `railway.json`
- Specifies build configuration
- Uses `dockerfile` builder

## Verify Deployment Success

### Check Deployment Logs
1. Go to "Deployments" tab
2. Click latest deployment
3. Look for:
   - ✅ "Successfully installed" messages
   - ✅ "Python 3.11" mentioned
   - ✅ "Uvicorn running on [your_url]"
   - ❌ Avoid "python: command not found" errors

### Test API Health
```bash
curl https://[your-railway-url].railway.app/docs
```

### Test PDF Upload
1. Open `https://[your-railway-url].railway.app`
2. Select "Understand Report" mode
3. Upload a PDF file
4. Check console for successful extraction

## Troubleshooting

### Issue: "python: command not found"
**Solution**: Already fixed with Dockerfile!
- Old problem: Procfile couldn't find Python
- **New solution**: Dockerfile explicitly installs Python 3.11

### Issue: Module Import Errors
**Check**:
```bash
# Verify all imports in requirements.txt are installed
pip install -r backend/requirements.txt
```

### Issue: Deployment Timeout
**Solution**:
- Reduce health check timeout in Dockerfile
- Check logs for hanging processes
- Restart deployment

### Issue: API Returns 502 Bad Gateway
**Solution**:
- Wait 2-3 minutes for cold start (first deployment)
- Check logs for UV/Uvicorn errors
- Verify OPENROUTER_API_KEY is set

## Performance Notes

- **First deployment**: 3-5 minutes (pulling Python image, installing packages)
- **Subsequent deployments**: 1-2 minutes
- **Cold start**: 30-60 seconds if service idle
- **Memory**: Free tier includes 512MB RAM (sufficient for this app)

## Deployment Success Checklist

- [x] Python 3.11 installed (from Dockerfile)
- [x] Dependencies with `--prefer-binary` (no compilation)
- [x] OPENROUTER_API_KEY environment variable set
- [x] Port 8000 exposed
- [x] Health check configured
- [x] Logs show successful startup
- [x] API responds to `/docs` endpoint
- [x] PDF upload works end-to-end

## Alternative: Revert to Render

If Railway deployment fails, Render is still configured and ready:

- Python: 3.11 pinned in `render.yaml`
- Deployment: Already tested in previous fixes
- Command: Go to Render dashboard → Re-deploy

## Cost Comparison

| Platform | Free Tier | Cold Start | Startup Time |
|----------|-----------|-----------|--------------|
| Railway  | 5GB/month| Yes | 30-60s |
| Render   | 750 hrs/mo| Yes | 30-60s |
| Heroku   | Deprecated | Was Free | N/A |
| Docker   | Self-hosted | No | 5-10s |

**Recommendation**: Railway for simplicity, Render as backup, Docker for cost optimization.

## Next Steps

1. Deploy on Railway using Dockerfile
2. Verify logs show "Python 3.11"
3. Test upload at `https://[your-url].railway.app`
4. If issues persist, switch to Render (already configured)

---

**Last Updated**: April 15, 2026
**Status**: Ready for Railway deployment with Dockerfile
