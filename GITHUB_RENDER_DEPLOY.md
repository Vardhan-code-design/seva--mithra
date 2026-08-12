# Seva Mithra — GitHub + Render Deployment

## Important
GitHub stores your code. It does not run a Flask server by itself.
Use GitHub + Render:

GitHub repository → Render Web Service → live website

## 1. Create GitHub repository

On GitHub:
1. Click `+` → `New repository`.
2. Repository name: `seva-mithra`
3. Choose Public if this is a college/demo project, otherwise Private.
4. Create repository.

## 2. Upload the project

Extract this ZIP on your laptop.

Open the project folder in VS Code.

Open Terminal in the project folder and run:

```bash
git init
git add .
git commit -m "Initial Seva Mithra website"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/seva-mithra.git
git push -u origin main
```

Replace `YOUR-GITHUB-USERNAME` with your GitHub username.

## 3. Deploy from GitHub using Render

1. Open Render.
2. Sign in with GitHub.
3. Choose `New` → `Web Service`.
4. Connect the `seva-mithra` GitHub repository.
5. Select branch `main`.
6. If Render detects `render.yaml`, use its configuration.

If entering the settings manually:
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn wsgi:application`

Render supports deploying Flask apps from GitHub and automatically redeploying when you push changes.

## 4. First deployment

Click `Create Web Service`.

After the build completes, Render gives you an address similar to:

`https://seva-mithra.onrender.com`

Open it and test:
- Home
- User registration
- Provider registration
- Login
- Service search
- Provider comparison
- Provider selection
- Booking
- Dashboards

## 5. Every future update

After changing the code:

```bash
git add .
git commit -m "Update Seva Mithra"
git push
```

Render automatically redeploys the linked branch.

## 6. Custom domain

When the Render URL works:

Render Dashboard → your service → Settings → Custom Domains → Add Custom Domain.

Enter your domain, for example:

`sevamithra.in`

Then update the DNS records at your domain provider exactly as Render shows.

Render automatically provisions and renews TLS certificates for custom domains.

## 7. Database warning

This project currently uses SQLite.

For a demonstration or small test deployment this is okay. For a real public service, use PostgreSQL because hosted application filesystems may not provide the persistent database storage you expect across deployments/restarts.

Before accepting real customers, migrate the database to PostgreSQL and add proper backups, email/OTP verification, rate limiting, logging and payment verification.

## 8. Do not upload secrets

Never commit:
- `.env`
- passwords
- API keys
- production database files

The project `.gitignore` already excludes `.env` and `seva_mithra.db`.
