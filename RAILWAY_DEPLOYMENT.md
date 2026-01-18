# Railway Deployment Guide for Route Handoff

This guide walks you through deploying the Route Handoff Django application on Railway.

## Prerequisites

- A Railway account (sign up at [railway.app](https://railway.app))
- Git installed on your local machine
- Your code committed to a Git repository (GitHub, GitLab, or local)

## Step-by-Step Deployment

### Step 1: Prepare Your Local Repository

1. **Initialize Git (if not already done):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Railway deployment"
   ```

2. **Create a `.gitignore` file** (if you don't have one):
   ```bash
   echo "db.sqlite3" >> .gitignore
   echo "*.pyc" >> .gitignore
   echo "__pycache__/" >> .gitignore
   echo ".env" >> .gitignore
   echo "venv/" >> .gitignore
   echo "staticfiles/" >> .gitignore
   git add .gitignore
   git commit -m "Add .gitignore"
   ```

### Step 2: Push to GitHub (Recommended)

1. **Create a new repository on GitHub:**
   - Go to [GitHub](https://github.com) and create a new repository
   - Don't initialize it with a README (if you already have one)

2. **Push your code:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Create Railway Project

1. **Sign in to Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub (recommended for easier integration)

2. **Create a New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo" (if you pushed to GitHub)
   - OR select "Empty Project" if deploying from local Git

3. **If using GitHub:**
   - Select your repository from the list
   - Railway will automatically detect it's a Django app

4. **If using Empty Project:**
   - Click "Empty Project"
   - Click "Add Service" → "GitHub Repo"
   - Select your repository

### Step 4: Configure Environment Variables

1. **In your Railway project dashboard:**
   - Click on your service
   - Go to the "Variables" tab

2. **Add the following environment variables:**

   **Required:**
   - `SECRET_KEY`: Generate a secure Django secret key
     - You can generate one using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
     - Or use any secure random string
   
   **Optional but recommended:**
   - `DEBUG`: Set to `False` for production
   - `ALLOWED_HOSTS`: Set to your Railway domain (e.g., `route-handoff-production.up.railway.app`)
     - Railway will provide this after deployment
     - You can also use `*` initially, but restrict it for security

   **Example values:**
   ```
   SECRET_KEY=your-generated-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=route-handoff-production.up.railway.app
   ```

### Step 5: Configure Build and Start Commands

Railway should auto-detect Django, but verify:

1. **In Railway dashboard → Settings:**
   - **Build Command:** (leave empty or use: `pip install -r requirements.txt`)
   - **Start Command:** Should be auto-detected from `Procfile`
     - If not, set to: `gunicorn route_handoff_project.wsgi --log-file -`

2. **Railway should automatically:**
   - Detect Python from `runtime.txt`
   - Use `Procfile` for start command
   - Install dependencies from `requirements.txt`

### Step 6: Set Up Database (PostgreSQL)

1. **Add PostgreSQL Database:**
   - In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
   - Railway will create a PostgreSQL database and provide connection details

2. **Get Database URL:**
   - Railway automatically creates a `DATABASE_URL` environment variable
   - It will be in the format: `postgresql://user:password@host:port/dbname`

3. **Update Django to use PostgreSQL:**
   - Railway should auto-detect `DATABASE_URL`
   - If not, you may need to install `psycopg2` or `psycopg2-binary`:
     ```bash
     # Add to requirements.txt
     psycopg2-binary>=2.9.0
     ```

4. **Update settings.py** (if Railway doesn't auto-detect):
   ```python
   import dj_database_url
   
   # In DATABASES section:
   DATABASES = {
       'default': dj_database_url.config(
           default=os.environ.get('DATABASE_URL'),
           conn_max_age=600
       )
   }
   ```
   - If you use this, add `dj-database-url>=2.1.0` to `requirements.txt`

### Step 7: Deploy

1. **Railway will automatically deploy when you:**
   - Push to your GitHub repository (if connected)
   - Or manually trigger deployment from Railway dashboard

2. **Monitor deployment:**
   - Go to the "Deployments" tab in Railway
   - Watch the build logs

3. **After successful deployment:**
   - Railway will provide a public URL (e.g., `route-handoff-production.up.railway.app`)
   - Click "Settings" → "Generate Domain" if you want a custom domain

### Step 8: Run Migrations

1. **Open Railway CLI or use Railway dashboard:**
   - Go to your service → "Deployments" → Click the latest deployment
   - Or use Railway CLI: `railway run python manage.py migrate`

2. **Run migrations:**
   - In Railway dashboard: Click "Deployments" → "View Logs" → Open shell
   - Or use the command: `python manage.py migrate`

3. **Create superuser (optional, for admin):**
   ```bash
   railway run python manage.py createsuperuser
   ```

### Step 9: Collect Static Files

Railway should handle this automatically via WhiteNoise middleware, but if needed:

```bash
railway run python manage.py collectstatic --noinput
```

### Step 10: Verify Deployment

1. **Visit your Railway URL:**
   - Click the URL provided by Railway
   - Test the application:
     - Add pickup/dropoff locations
     - Test navigation flow

2. **Check logs:**
   - Railway dashboard → "Deployments" → "View Logs"
   - Look for any errors

## Troubleshooting

### Common Issues:

1. **"Application Error" or 500 Error:**
   - Check Railway logs for detailed error messages
   - Verify `SECRET_KEY` is set
   - Ensure `DEBUG=False` in production
   - Check `ALLOWED_HOSTS` includes your Railway domain

2. **Static files not loading:**
   - Verify `whitenoise` is in `requirements.txt` and `MIDDLEWARE`
   - Run `collectstatic` if needed
   - Check `STATIC_ROOT` and `STATIC_URL` in settings

3. **Database connection errors:**
   - Verify PostgreSQL service is running
   - Check `DATABASE_URL` environment variable exists
   - Ensure migrations are run

4. **"DisallowedHost" error:**
   - Add your Railway domain to `ALLOWED_HOSTS` environment variable
   - Format: `your-app-name.up.railway.app` (no `https://`)

### Updating Your App:

1. **Make changes locally**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```
3. **Railway will automatically redeploy**

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Django secret key | Generated string |
| `DEBUG` | No | Debug mode | `False` |
| `ALLOWED_HOSTS` | Yes | Allowed hostnames | `your-app.up.railway.app` |
| `DATABASE_URL` | Auto | PostgreSQL connection | Auto-set by Railway |

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [WhiteNoise Documentation](https://whitenoise.readthedocs.io/)

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is set and secure
- [ ] `ALLOWED_HOSTS` is configured (not `*`)
- [ ] HTTPS is enabled (Railway provides this automatically)
- [ ] Database credentials are secure (Railway manages this)
- [ ] Static files are served securely (WhiteNoise handles this)

---

**Your app should now be live on Railway!** 🚀
