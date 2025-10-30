# Deployment Guide

This guide explains how to deploy the Smart Personal Trader to Railway.app (backend) and Netlify (frontend).

## Prerequisites

- GitHub account
- Railway.app account (free tier: $5 credit/month)
- Netlify account (free tier available)

## Backend Deployment (Railway.app)

### 1. Create Railway Project

1. Go to [Railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub repositories
5. Select your `selmastockprediction` repository
6. Choose the `claude/qlib-stock-predictor-011CUd7T3Ei3FtAzf3WU7vQr` branch (or your main branch)

### 2. Configure Backend Service

1. In Railway project settings, set the **Root Directory** to `backend`
2. Railway will automatically detect Python and use the configuration files:
   - `nixpacks.toml` - Specifies Python 3.12 and system dependencies
   - `runtime.txt` - Python version
   - `Procfile` - Start command
   - `railway.toml` - Railway-specific configuration

### 3. Set Environment Variables (Optional)

In Railway project settings > Variables, add:

```
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
```

### 4. Deploy

1. Railway will automatically build and deploy
2. Wait for deployment to complete (5-10 minutes first time)
3. Copy the **public URL** (e.g., `https://your-app.railway.app`)
4. Test by visiting `https://your-app.railway.app/health`

### 5. Verify Deployment

Check these endpoints:
- `https://your-app.railway.app/` - Root endpoint
- `https://your-app.railway.app/health` - Health check
- `https://your-app.railway.app/docs` - API documentation (FastAPI Swagger UI)

## Frontend Deployment (Netlify)

### 1. Create Netlify Site

1. Go to [Netlify](https://netlify.com)
2. Click "Add new site" > "Import an existing project"
3. Connect to GitHub and select your repository
4. Choose the branch to deploy

### 2. Configure Build Settings

**Build settings:**
- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `frontend/.next`
- Node version: 18

### 3. Set Environment Variables

In Netlify site settings > Environment variables, add:

```
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app
NEXT_PUBLIC_DEFAULT_STOCK=BBCA
```

**IMPORTANT:** Replace `https://your-railway-backend-url.railway.app` with your actual Railway backend URL from step 1.

### 4. Deploy

1. Click "Deploy site"
2. Wait for build to complete (3-5 minutes)
3. Your site will be available at `https://your-site-name.netlify.app`

### 5. Custom Domain (Optional)

To use a custom domain like `selmastock.netlify.app`:
1. Go to Site settings > Domain management
2. Click "Add custom domain"
3. Follow the instructions to configure DNS

## Post-Deployment Configuration

### Update Backend CORS

After deploying frontend, update the backend CORS settings:

1. In Railway backend, add environment variable:
```
CORS_ORIGINS=["https://your-netlify-site.netlify.app"]
```

2. Or edit `backend/config.py` and redeploy:
```python
cors_origins: list = Field(
    default=[
        "http://localhost:3000",
        "https://selmastock.netlify.app",  # Add your Netlify URL
    ]
)
```

### Test Integration

1. Visit your Netlify frontend URL
2. The dashboard should load without errors
3. Try selecting a stock (BBCA, BMRI, etc.)
4. Click "Generate Prediction"
5. Verify predictions appear with BUY/HOLD/SELL signals

## Troubleshooting

### Railway Backend Issues

**Issue: Container crashes with "libgomp.so.1 not found"**
- Solution: Already fixed with `nixpacks.toml` configuration
- Verify `nixpacks.toml` exists in backend folder

**Issue: Python 3.13 compatibility errors**
- Solution: Use Python 3.12 (specified in `.python-version` and `runtime.txt`)
- Railway will automatically use the correct version

**Issue: Models not training**
- Check Railway logs for errors
- Ensure at least 512MB RAM allocated
- First prediction will be slow (training takes 2-5 minutes)

### Netlify Frontend Issues

**Issue: Page shows "404" or blank**
- Verify build command: `npm run build`
- Check Netlify build logs for errors
- Ensure base directory is set to `frontend`

**Issue: "Failed to fetch" or API errors**
- Verify `NEXT_PUBLIC_API_URL` environment variable is set correctly
- Check Railway backend is running at the URL
- Verify CORS is configured on backend

**Issue: Environment variables not working**
- Netlify requires variables to start with `NEXT_PUBLIC_`
- Redeploy after adding environment variables

## Monitoring

### Railway Monitoring

- View logs in Railway dashboard > Deployments > View logs
- Monitor resource usage (CPU, RAM)
- Check activity logs at `/api/activity/logs/summary`

### Netlify Monitoring

- View build logs in Netlify dashboard > Deploys
- Check function logs if using serverless functions
- Monitor bandwidth and build minutes

## Cost Estimates

### Railway.app
- Free tier: $5 credit/month
- Estimated usage: ~$8-12/month for 24/7 deployment
- Includes: 512MB RAM, shared CPU, 1GB storage

### Netlify
- Free tier: Unlimited (with limits)
- 100GB bandwidth/month
- 300 build minutes/month
- Sufficient for personal use

**Total estimated cost: $3-7/month** (Railway charges $8-12, minus $5 free credit)

## Scheduled Tasks (Coming Soon)

Once both are deployed, we'll add:
- Daily predictions at 6 AM WIB (Railway cron job)
- Weekly model retraining Sunday 2 AM WIB
- Automatic portfolio value updates

These will be configured using Railway's cron job feature or a separate scheduler service.

## Security Notes

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use environment variables** for sensitive data
3. **Keep Railway and Netlify logs private**
4. **Monitor API usage** to prevent abuse
5. **Set up rate limiting** if public (future enhancement)

## Support

If you encounter issues:
1. Check Railway build logs
2. Check Netlify deploy logs
3. Test backend endpoint directly: `curl https://your-backend.railway.app/health`
4. Verify environment variables are set correctly
