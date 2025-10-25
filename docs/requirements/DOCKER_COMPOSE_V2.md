# Docker Compose v2 Requirements

## 🐳 Docker Compose v2.0+ Required

GraphMind requires **Docker Compose v2.0+** which uses the modern `docker compose` command (not the legacy `docker-compose` command).

## ✅ Check Your Version

```bash
# Check Docker Compose version
docker compose version

# Should show: Docker Compose version v2.x.x
```

## 🔧 Installation

### Ubuntu/Debian
```bash
# Install Docker Compose v2
sudo apt update
sudo apt install docker-compose-plugin

# Verify installation
docker compose version
```

### CentOS/RHEL/Fedora
```bash
# Install Docker Compose v2
sudo yum install docker-compose-plugin

# Or on newer systems
sudo dnf install docker-compose-plugin

# Verify installation
docker compose version
```

### macOS
```bash
# Install via Homebrew
brew install docker-compose

# Or install Docker Desktop (includes Compose v2)
# Download from: https://www.docker.com/products/docker-desktop
```

### Windows
```bash
# Install Docker Desktop (includes Compose v2)
# Download from: https://www.docker.com/products/docker-desktop
```

## 🚫 Legacy Docker Compose (v1.x)

**DO NOT USE** the legacy `docker-compose` command (v1.x). GraphMind requires the modern Docker Compose v2.

### Migration from v1.x
```bash
# Old way (v1.x) - DON'T USE
docker-compose up -d

# New way (v2.x) - USE THIS
docker compose up -d
```

## 🔍 Troubleshooting

### "docker-compose: command not found"
```bash
# This means you have v1.x or no Compose
# Install Docker Compose v2 plugin
sudo apt install docker-compose-plugin
```

### "docker compose: command not found"
```bash
# This means Docker Compose v2 is not installed
# Install the plugin
sudo apt install docker-compose-plugin
```

### Version Check
```bash
# Check if you have v2
docker compose version

# Should show: Docker Compose version v2.x.x
# NOT: docker-compose version 1.x.x
```

## 📋 GraphMind Commands

All GraphMind deployment commands use Docker Compose v2:

```bash
# Deploy GraphMind
./scripts/deploy-graphmind.sh

# Manual deployment
docker compose -f docker-compose.graphmind.yml up -d

# View logs
docker compose -f docker-compose.graphmind.yml logs -f

# Stop services
docker compose -f docker-compose.graphmind.yml down

# Restart services
docker compose -f docker-compose.graphmind.yml restart
```

## 🎯 Why Docker Compose v2?

### Benefits
- **Modern Architecture**: Built into Docker CLI
- **Better Performance**: Faster startup and operations
- **Enhanced Security**: Better security model
- **Active Development**: Ongoing updates and improvements
- **Future-Proof**: v1.x is deprecated

### GraphMind Requirements
- **Security**: v2 provides better network isolation
- **Performance**: Faster container orchestration
- **Compatibility**: Works with modern Docker features
- **Maintenance**: Active support and updates

## 🔧 System Requirements

### Minimum Requirements
- **Docker**: 20.10+
- **Docker Compose**: v2.0+
- **OS**: Linux, macOS, Windows
- **RAM**: 8GB+ (32GB+ recommended)
- **Storage**: 50GB+ free space

### Recommended Setup
- **Docker**: Latest stable version
- **Docker Compose**: v2.20+ (latest)
- **OS**: Ubuntu 22.04+ or macOS 12+
- **RAM**: 32GB+
- **Storage**: 100GB+ SSD
- **GPU**: NVIDIA with 24GB+ VRAM (for LLM inference)

## 📚 Additional Resources

- [Docker Compose v2 Documentation](https://docs.docker.com/compose/)
- [Migration Guide from v1 to v2](https://docs.docker.com/compose/migrate/)
- [Docker Compose CLI Reference](https://docs.docker.com/compose/reference/)

---

**Note**: GraphMind deployment scripts automatically check for Docker Compose v2 and provide helpful error messages if the wrong version is detected.
