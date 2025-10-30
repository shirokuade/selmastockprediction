# Smart Personal Trader - Scheduler & Configuration Guide

This guide explains how to configure and use the automated scheduler for daily predictions and weekly model retraining.

## Table of Contents

1. [Overview](#overview)
2. [Scheduler Features](#scheduler-features)
3. [Configuration](#configuration)
4. [API Endpoints](#api-endpoints)
5. [Monitoring](#monitoring)
6. [Manual Triggers](#manual-triggers)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Smart Personal Trader includes an automated scheduler that runs background jobs for:
- **Daily Predictions** (6 AM WIB) - Generate predictions for all portfolio stocks
- **Weekly Retraining** (Sunday 2 AM WIB) - Retrain all models with 5 years of historical data

The scheduler starts automatically when the backend starts and runs 24/7 in the cloud.

---

## Scheduler Features

### Daily Prediction Routine (6 AM WIB)

**Schedule**: Every day at 6:00 AM Western Indonesian Time (WIB)

**Tasks Performed**:
1. Fetch list of stocks in user's portfolio
2. Fetch latest hourly data for each stock
3. Generate predictions using ensemble model (XGBoost, LightGBM, Random Forest)
4. Calculate BUY/HOLD/SELL trading signals
5. Log all activities to activity logs

**Duration**: Approximately 2-5 minutes (depends on number of stocks)

**Output**:
- Predictions stored in memory
- Activity logs created for each prediction
- Summary log with successful/failed predictions

### Weekly Retraining Routine (Sunday 2 AM WIB)

**Schedule**: Every Sunday at 2:00 AM Western Indonesian Time (WIB)

**Tasks Performed**:
1. Get all stocks (portfolio + default stocks: BBCA, BMRI, BBRI, TLKM, ASII)
2. Fetch 5 years of daily historical data for each stock
3. Train all 3 ensemble models (XGBoost, LightGBM, Random Forest)
4. Save updated model files to disk
5. Log training completion with metrics

**Duration**: Approximately 10-30 minutes (depends on number of stocks)

**Output**:
- Updated `.pkl` model files in `./models/` directory
- Activity logs for each stock trained
- Summary log with training statistics

---

## Configuration

### Timezone Settings

The scheduler uses **Asia/Jakarta (WIB)** timezone by default.

To change timezone, edit `backend/services/scheduler.py`:

```python
self.timezone = pytz.timezone('Asia/Jakarta')  # Change to your timezone
```

Available timezones: `Asia/Singapore`, `Asia/Tokyo`, `UTC`, etc.

### Schedule Customization

To change schedule times, edit the cron triggers in `backend/services/scheduler.py`:

**Daily Routine:**
```python
# Current: 6 AM WIB
CronTrigger(hour=6, minute=0, timezone=self.timezone)

# Example: Change to 8 AM
CronTrigger(hour=8, minute=0, timezone=self.timezone)
```

**Weekly Routine:**
```python
# Current: Sunday 2 AM WIB
CronTrigger(day_of_week='sun', hour=2, minute=0, timezone=self.timezone)

# Example: Change to Monday 3 AM
CronTrigger(day_of_week='mon', hour=3, minute=0, timezone=self.timezone)
```

### Environment Variables

You can control scheduler behavior with these optional environment variables:

```bash
# Disable scheduler (for testing)
SCHEDULER_ENABLED=false

# Adjust prediction days
DEFAULT_PREDICTION_DAYS=5

# Training data period
TRAINING_PERIOD_DAYS=1825  # 5 years
```

---

## API Endpoints

### Get Scheduler Status

```bash
GET /api/scheduler/status
```

**Response:**
```json
{
  "status": "running",
  "timezone": "Asia/Jakarta (WIB)",
  "schedules": {
    "daily_prediction": {
      "description": "Generate predictions for portfolio stocks",
      "schedule": "Every day at 6:00 AM WIB",
      "next_run": "2025-10-31 06:00:00 WIB"
    },
    "weekly_retrain": {
      "description": "Retrain all models with 5 years data",
      "schedule": "Every Sunday at 2:00 AM WIB",
      "next_run": "2025-11-03 02:00:00 WIB"
    }
  }
}
```

### Manual Trigger - Daily Routine

```bash
POST /api/scheduler/trigger/daily
```

Manually trigger the daily prediction routine. Useful for testing or running predictions on-demand.

**Response:**
```json
{
  "success": true,
  "message": "Daily prediction routine triggered successfully",
  "note": "Check activity logs for progress"
}
```

### Manual Trigger - Weekly Routine

```bash
POST /api/scheduler/trigger/weekly
```

Manually trigger the weekly retraining routine. ⚠️ Warning: This may take 10-30 minutes.

**Response:**
```json
{
  "success": true,
  "message": "Weekly retraining routine triggered successfully",
  "warning": "This process may take 10-30 minutes",
  "note": "Check activity logs for progress"
}
```

### List All Jobs

```bash
GET /api/scheduler/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "id": "daily_prediction",
      "name": "Daily Prediction Routine (6 AM WIB)",
      "next_run": "2025-10-31 06:00:00 WIB",
      "trigger": "cron[hour=6, minute=0]"
    },
    {
      "id": "weekly_retrain",
      "name": "Weekly Model Retraining (Sunday 2 AM WIB)",
      "next_run": "2025-11-03 02:00:00 WIB",
      "trigger": "cron[day_of_week=sun, hour=2, minute=0]"
    }
  ],
  "total": 2
}
```

---

## Monitoring

### View Activity Logs

**Frontend**: Go to **Settings** page → **Activity Logs** section

**API**: `GET /api/activity/logs?limit=50`

**Filter by Type**:
- `daily_update` - Daily prediction summaries
- `weekly_retrain` - Weekly training summaries
- `prediction` - Individual predictions
- `training` - Individual model training
- `error` - Errors and failures

### Check Scheduler Status

**Frontend**: Coming soon - Scheduler status widget on Dashboard

**API**: `GET /api/scheduler/status`

### View Logs in Railway

1. Go to Railway dashboard
2. Select your project
3. Click on the service
4. Go to **Deployments** → **View Logs**
5. Look for scheduler log messages:
   ```
   Scheduler started successfully
   Daily predictions scheduled: Every day at 6:00 AM WIB
   Starting daily prediction routine at 2025-10-31 06:00:00 WIB
   ```

---

## Manual Triggers

### Via Frontend (Coming Soon)

A scheduler control panel will be added to the Settings page.

### Via API

**Trigger Daily Routine:**
```bash
curl -X POST https://your-backend.railway.app/api/scheduler/trigger/daily
```

**Trigger Weekly Routine:**
```bash
curl -X POST https://your-backend.railway.app/api/scheduler/trigger/weekly
```

### Via Railway Console

1. Go to Railway dashboard
2. Select your project
3. Click **Variables**
4. Add variable: `TRIGGER_DAILY=true`
5. Redeploy the service

---

## Troubleshooting

### Scheduler Not Starting

**Symptoms**: No scheduled jobs in logs, `/api/scheduler/status` returns empty

**Solutions**:
1. Check Railway logs for errors during startup
2. Verify `APScheduler>=3.10.4` is in requirements.txt
3. Ensure Railway service has enough RAM (512MB minimum)
4. Check if environment variable `SCHEDULER_ENABLED=false` is set

**Fix**: Redeploy with updated requirements

### Daily Routine Failing

**Symptoms**: Activity logs show errors like "Failed to fetch data" or "Model not found"

**Solutions**:
1. Check if models are trained: `GET /api/prediction/model-status/{symbol}`
2. Manually trigger weekly retraining to train models
3. Check internet connectivity (Yahoo Finance API)
4. Verify stock symbols in portfolio are valid

**Fix**: Run manual weekly retraining

### Weekly Retraining Taking Too Long

**Symptoms**: Routine takes more than 1 hour

**Solutions**:
1. Reduce number of stocks in portfolio
2. Check Railway CPU/RAM usage
3. Consider upgrading Railway plan
4. Split training into batches (custom development needed)

**Optimization**: Train only portfolio stocks, not all default stocks

### Timezone Issues

**Symptoms**: Jobs running at wrong time

**Solutions**:
1. Verify Railway server timezone: Check logs for "WIB" suffix
2. Update timezone in scheduler.py if needed
3. Convert times: WIB = UTC+7

**Example**:
- 6 AM WIB = 11 PM UTC (previous day)
- 2 AM WIB = 7 PM UTC (previous day)

### Out of Memory

**Symptoms**: Service crashes during training, "OOMKilled" in logs

**Solutions**:
1. Upgrade Railway plan (more RAM)
2. Reduce training data period from 5 years to 3 years
3. Train fewer stocks per batch
4. Use more efficient models (disable one model from ensemble)

**Quick Fix**: Edit `config.py`:
```python
training_period: int = 1095  # 3 years instead of 5
```

---

## Advanced Configuration

### Customize Prediction Logic

Edit `backend/services/scheduler.py` → `daily_prediction_routine()`:

```python
# Change prediction days
result = await self.predictor.predict(symbol, days=7)  # Default: 5

# Add custom filters
if result.confidence < 0.7:
    continue  # Skip low-confidence predictions
```

### Customize Training Logic

Edit `backend/services/scheduler.py` → `weekly_retraining_routine()`:

```python
# Train only portfolio stocks (skip defaults)
all_stocks = portfolio_stocks  # Remove: + default_stocks

# Adjust training delay
await asyncio.sleep(10)  # Default: 5 seconds
```

### Add Custom Schedules

Add new job in `backend/services/scheduler.py` → `start()`:

```python
# Monthly report: First day of month, 9 AM
self.scheduler.add_job(
    self.monthly_report_routine,
    trigger=CronTrigger(day=1, hour=9, minute=0, timezone=self.timezone),
    id='monthly_report',
    name='Monthly Performance Report'
)
```

---

## Best Practices

1. **Monitor Regularly**: Check activity logs daily for errors
2. **Test Before Deploy**: Use manual triggers to test routines
3. **Keep Models Updated**: Ensure weekly retraining completes successfully
4. **Manage Portfolio**: Remove stocks you're not tracking to reduce load
5. **Set Alerts**: Use Railway notifications for deployment failures
6. **Backup Data**: Railway provides automatic backups, but export important data
7. **Review Signals**: Don't blindly follow signals, use them as guidance

---

## Support

### Check System Health

```bash
# Backend health
curl https://your-backend.railway.app/health

# Scheduler status
curl https://your-backend.railway.app/api/scheduler/status

# Recent activity
curl https://your-backend.railway.app/api/activity/logs?limit=10
```

### Get Help

- **Railway Logs**: Check deployment logs for errors
- **Activity Logs**: View detailed operation history
- **API Docs**: Visit `/docs` endpoint for Swagger UI
- **GitHub Issues**: Report bugs or request features

---

## Example Workflow

### Daily Routine at 6 AM WIB

```
06:00:00 - Scheduler triggers daily_prediction_routine()
06:00:01 - Get portfolio stocks: [BBCA, BMRI, TLKM]
06:00:02 - Processing BBCA...
06:00:15 - ✓ BBCA: BUY signal (Confidence: 78%)
06:00:17 - Processing BMRI...
06:00:30 - ✓ BMRI: HOLD signal (Confidence: 82%)
06:00:32 - Processing TLKM...
06:00:45 - ✓ TLKM: SELL signal (Confidence: 75%)
06:00:47 - Daily routine completed: 3 successful, 0 failed (47s)
```

### Weekly Retraining at 2 AM Sunday

```
02:00:00 - Scheduler triggers weekly_retraining_routine()
02:00:01 - Stocks to train: [BBCA, BMRI, BBRI, TLKM, ASII]
02:00:02 - Training BBCA (5 years daily data)...
02:05:30 - ✓ BBCA: Training completed
02:05:35 - Training BMRI...
02:11:10 - ✓ BMRI: Training completed
02:11:15 - Training BBRI...
02:16:50 - ✓ BBRI: Training completed
02:16:55 - Training TLKM...
02:22:30 - ✓ TLKM: Training completed
02:22:35 - Training ASII...
02:28:10 - ✓ ASII: Training completed
02:28:15 - Weekly retraining completed: 5 successful, 0 failed (1695s)
```

---

## Conclusion

The automated scheduler enables 24/7 operation of your Smart Personal Trader, continuously monitoring your portfolio and keeping models up-to-date. Regularly check activity logs and monitor performance to ensure optimal operation.

For any issues or questions, check the troubleshooting section or consult the API documentation at `/docs`.
