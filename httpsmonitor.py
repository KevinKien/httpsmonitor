import os
import requests
import ssl
import OpenSSL
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import datetime, timedelta
import socket

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SUBDOMAIN_FILE_PATH = os.getenv('SUBDOMAIN_FILE_PATH')

def main():
    with open(SUBDOMAIN_FILE_PATH, 'r') as file:
        for line in file:
            domain = line.strip()
            if domain:
                print(f"Processing domain: {domain}")
                check_domain(domain)

def check_domain(domain):
    url = f"https://{domain}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        cert = response.raw.connection.sock.getpeercert(binary_form=True)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
        if is_cert_expiring_soon(x509):
            send_telegram_notification(domain, "Certificate expiring soon")

        check_ssl_versions(domain)
        
    except requests.RequestException as e:
        print(f"No HTTPS or error checking domain {domain}: {e}")
        send_telegram_notification(domain, "No HTTPS or error occurred")

def check_ssl_versions(domain):
    ssl_versions = [
        ("SSLv3", ssl.PROTOCOL_SSLv3),
        ("TLS 1.0", ssl.PROTOCOL_TLSv1),
        ("TLS 1.1", ssl.PROTOCOL_TLSv1_1),
        ("TLS 1.2", ssl.PROTOCOL_TLSv1_2),
        ("TLS 1.3", ssl.PROTOCOL_TLS),
    ]

    for version_name, ssl_version in ssl_versions:
        supported = check_tls_version(domain, ssl_version)
        status = "supported" if supported else "not supported"
        print(f"Domain {domain}: {version_name} {status}")
        if not supported and ssl_version == ssl.PROTOCOL_TLS:
            send_telegram_notification(domain, f"{version_name} is not supported")

def check_tls_version(domain, ssl_version):
    try:
        context = ssl.SSLContext(ssl_version)
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
        conn.settimeout(5.0)
        conn.connect((domain, 443))
        conn.close()
        return True
    except ssl.SSLError:
        return False
    except socket.error:
        return False

def is_cert_expiring_soon(cert):
    now = datetime.utcnow()
    expiry_threshold = now + timedelta(days=7)  # 7 days from now
    expiry_date = datetime.strptime(cert.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ')
    return expiry_date < expiry_threshold

def send_telegram_notification(domain, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': f"Domain: {domain}\nIssue: {message}"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending notification: {e}")

if __name__ == "__main__":
    main()
