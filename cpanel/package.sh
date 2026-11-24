#!/bin/sh
# Builds dist/enaks-cpanel.zip for upload to Namecheap cPanel public_html (extract in place).
set -e; cd "$(dirname "$0")/.."
python3 build.py --site-url https://eautoandtransport.com
rm -rf dist/stage && mkdir -p dist/stage/api
cp -R public/. dist/stage/ && cp cpanel/.htaccess dist/stage/ && cp cpanel/api/request.php dist/stage/api/
(cd dist/stage && rm -f ../enaks-cpanel.zip && zip -qr ../enaks-cpanel.zip . -x '.DS_Store')
echo "dist/enaks-cpanel.zip ready"
