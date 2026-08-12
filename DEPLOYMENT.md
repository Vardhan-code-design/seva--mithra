# Seva Mithra — Professional Deployment

Recommended architecture:

Browser → Domain/DNS → Nginx → HTTPS → Gunicorn → Flask → SQLite

## 1. Buy a domain
Choose a domain such as:
- sevamithra.in
- sevamithraapp.in
- getsevamithra.in

Use any registrar you prefer.

## 2. Rent a VPS
For the current project, a small Ubuntu VPS is enough for an initial launch.
Choose a VPS provider with a data center close to your users.

## 3. Point the domain to the VPS
Create:
- A record: `@` → YOUR_SERVER_IP
- A record: `www` → YOUR_SERVER_IP

DNS propagation can take some time.

## 4. Upload the project
Upload this project to:
`/var/www/seva-mithra`

## 5. Install Python and dependencies
Run:
```bash
cd /var/www/seva-mithra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 6. Create the secret
Create `/var/www/seva-mithra/.env`:
```text
SECRET_KEY=PUT-A-LONG-RANDOM-SECRET-HERE
```

Never publish `.env`.

## 7. Test Gunicorn
```bash
cd /var/www/seva-mithra
.venv/bin/gunicorn -c gunicorn.conf.py wsgi:application
```

## 8. Configure systemd
Copy:
`deployment/seva-mithra.service`
to:
`/etc/systemd/system/seva-mithra.service`

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now seva-mithra
sudo systemctl status seva-mithra
```

## 9. Configure Nginx
Edit `deployment/seva-mithra.nginx` and replace `YOURDOMAIN` with the real domain.

Copy it to:
`/etc/nginx/sites-available/seva-mithra`

Then:
```bash
sudo ln -s /etc/nginx/sites-available/seva-mithra /etc/nginx/sites-enabled/seva-mithra
sudo nginx -t
sudo systemctl reload nginx
```

## 10. Enable HTTPS
After the domain points to the VPS:
```bash
sudo certbot --nginx -d YOURDOMAIN -d www.YOURDOMAIN
```

Choose the redirect-to-HTTPS option.

## 11. Important production notes
- Do not use `python app.py` as the production server.
- Use Gunicorn behind Nginx.
- Keep the Flask secret in `.env`.
- Back up `seva_mithra.db` regularly.
- For higher traffic/multiple servers, migrate from SQLite to PostgreSQL.
- Before accepting real payments, add a proper payment gateway and server-side payment verification.
- Before public launch, add email/OTP verification, rate limiting, backups and monitoring.

## Health checks
```bash
sudo systemctl status seva-mithra
sudo journalctl -u seva-mithra -n 100 --no-pager
sudo nginx -t
```
