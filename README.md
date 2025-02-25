## Installation 
1. Install MySQL
```bash
sudo apt install mysql-server
```
2. Install the Python 3 and MySQL development headers and libraries
```bash
sudo apt install python3-dev default-libmysqlclient-dev build-essential pkg-config
```
3. Install LDAP
```bash
sudo apt install python3-dev libldap2-dev libsasl2-dev libssl-dev
```
4. Tools to render HTML into PDF
```bash
sudo apt install wkhtmltopdf
```

## Requirements
```bash
pip install django mysqlclient pillow qrcode[PIL] django-auth-ldap imgkit
```
## Note
You can only use your camera to scan a QR code when using HTTPS
