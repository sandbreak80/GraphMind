# Security Guide

This document outlines security considerations and best practices for the EminiPlayer RAG service.

## 🔒 Security Overview

The EminiPlayer RAG service is designed to run locally with minimal external dependencies, prioritizing data privacy and security.

## 🛡️ Data Protection

### Local Processing
- **No external API calls** for core functionality
- **All processing happens locally** in Docker containers
- **Documents are never transmitted** to external services
- **Vector embeddings** are stored locally in ChromaDB

### Document Access
- Documents are mounted as **read-only** volumes
- Only the configured `DOCUMENTS_DIR` is accessible
- No write access to source documents
- Temporary processing files are isolated in containers

## 🔐 Environment Security

### Environment Variables
```bash
# CRITICAL: Never commit these files
.env
.env.local
.env.production
.env.staging

# Use the template instead
.env.template  # Safe to commit
```

### File Permissions
```bash
# Set restrictive permissions on environment files
chmod 600 .env
chown $USER:$USER .env
```

### Secrets Management
- **No hardcoded credentials** in the codebase
- **All sensitive data** stored in environment variables
- **API keys** (if used) should be in `.env` files only
- **Database credentials** (if used) should be environment-based

## 🌐 Network Security

### Local-Only Operation
- Service runs on `localhost:8001` by default
- **No external network access** required for core functionality
- Ollama connection is local-only (`localhost:11434`)
- Docker containers use internal networking

### Firewall Considerations
```bash
# Optional: Restrict access to localhost only
sudo ufw allow from 127.0.0.1 to any port 8001
sudo ufw deny 8001
```

## 🐳 Container Security

### Docker Security
- **Non-root user** in containers where possible
- **Read-only filesystem** for document access
- **Minimal base images** to reduce attack surface
- **No unnecessary packages** installed

### Volume Security
```yaml
# Documents are mounted read-only
volumes:
  - ${DOCUMENTS_DIR}:/workspace/pdfs:ro  # Read-only access
  - chroma-data:/workspace/chroma_db     # Persistent storage
  - ${OUTPUT_DIR}:/workspace/outputs     # Output only
```

## 📁 File System Security

### Directory Structure
```
EminiPlayer/
├── .env                    # ❌ Never commit (contains secrets)
├── .env.template          # ✅ Safe to commit (template only)
├── documents/             # ❌ Never commit (your data)
├── outputs/               # ❌ Never commit (generated content)
├── chroma_data/           # ❌ Never commit (vector database)
└── app/                   # ✅ Safe to commit (source code)
```

### .gitignore Protection
The `.gitignore` file protects sensitive data:
```gitignore
# Environment and secrets
.env
.env.local
.env.production
.env.staging
*.key
*.pem
*.p12
*.pfx

# Local data directories
rag_docs_zone/
pdfs/
documents/
data/

# Generated content
outputs/
chroma_db/
chroma_data/
*.log
```

## 🔍 Security Audit Checklist

Before deploying, verify:

- [ ] `.env` file is not committed to version control
- [ ] All hardcoded paths removed from codebase
- [ ] Document directory has appropriate permissions
- [ ] Docker containers run with minimal privileges
- [ ] No external API keys in source code
- [ ] Network access is restricted to localhost
- [ ] Log files don't contain sensitive information
- [ ] Output files are properly excluded from version control

## 🚨 Incident Response

### If Secrets Are Exposed
1. **Immediately rotate** any exposed credentials
2. **Remove sensitive data** from git history if needed
3. **Update .gitignore** to prevent future exposure
4. **Audit access logs** for unauthorized access

### Data Breach Response
1. **Stop the service** immediately
2. **Isolate the system** from network access
3. **Preserve logs** for forensic analysis
4. **Notify stakeholders** as required
5. **Review and update** security measures

## 🔧 Security Hardening

### Additional Measures
```bash
# Use Docker secrets for production
echo "your-secret" | docker secret create ollama_key -

# Enable Docker content trust
export DOCKER_CONTENT_TRUST=1

# Use specific image tags (not 'latest')
docker pull eminiplayer:1.0.0
```

### Monitoring
```bash
# Monitor container resource usage
docker stats emini-rag

# Check for unusual network activity
docker exec emini-rag netstat -tuln

# Review container logs for anomalies
docker-compose logs rag-service | grep -i error
```

## 📋 Compliance Notes

### Data Privacy
- **No personal data** is transmitted externally
- **All processing** happens on your infrastructure
- **You control** all data storage and retention
- **No third-party** data sharing

### Audit Trail
- **All operations** are logged
- **Document processing** is tracked
- **API requests** are recorded
- **Error conditions** are captured

## 🆘 Security Support

If you discover a security vulnerability:

1. **Do not** create a public issue
2. **Contact** the maintainer privately
3. **Provide** detailed reproduction steps
4. **Allow** reasonable time for response

## 📚 Additional Resources

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Container Security](https://owasp.org/www-project-container-security/)
- [Environment Variable Security](https://12factor.net/config)
