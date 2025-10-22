#!/bin/bash

# Generate SSL certificates for emini.riffyx.com
# This script creates self-signed certificates for development/testing
# For production, replace with real certificates from Let's Encrypt or your CA

echo "🔐 Generating SSL certificates for emini.riffyx.com..."

# Create SSL directory
mkdir -p ssl

# Generate private key
openssl genrsa -out ssl/key.pem 2048

# Generate certificate signing request
openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=emini.riffyx.com"

# Generate self-signed certificate
openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem

# Set proper permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

# Clean up CSR
rm ssl/cert.csr

echo "✅ SSL certificates generated successfully!"
echo "📁 Certificates saved to: nginx/ssl/"
echo "🔑 Private key: nginx/ssl/key.pem"
echo "📜 Certificate: nginx/ssl/cert.pem"
echo ""
echo "⚠️  Note: These are self-signed certificates for development."
echo "   For production, replace with real certificates from Let's Encrypt."
echo ""
echo "🚀 To use Let's Encrypt certificates:"
echo "   1. Install certbot: sudo apt install certbot"
echo "   2. Generate certificates: sudo certbot certonly --standalone -d emini.riffyx.com"
echo "   3. Copy certificates to nginx/ssl/"
echo "   4. Update nginx.conf with correct paths"