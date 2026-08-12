#!/usr/bin/env bash
set -e

APP_DIR="/var/www/seva-mithra"

sudo apt update
sudo apt install -y python3 python3-venv nginx certbot python3-certbot-nginx

sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER:$USER" "$APP_DIR"

cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Create .env with a strong SECRET_KEY before starting the service."
echo "Then install deployment/seva-mithra.service and deployment/seva-mithra.nginx."
