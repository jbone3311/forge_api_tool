# Troubleshooting Guide - Forge-API-Tool

## 🎯 Overview
This guide provides comprehensive troubleshooting procedures for common issues encountered with the Forge-API-Tool, including diagnostic steps, solutions, and preventive measures.

## 🔍 Diagnostic Tools

### Built-in Diagnostic Commands
```bash
# Test API connectivity
python cli.py api test

# Validate configuration
python cli.py config validate

# Check system health
python cli.py system health

# Run diagnostics
python cli.py system diagnose

# Check dependencies
python cli.py system dependencies
```

### Log Analysis
```bash
# View application logs
tail -f logs/app.log

# View error logs
grep -i error logs/app.log

# View API logs
grep -i api logs/app.log

# View performance logs
grep -i performance logs/app.log

# View recent logs
tail -n 100 logs/app.log
```

### System Monitoring
```bash
# Check system resources
htop
free -h
df -h

# Check network connectivity
ping api.forge.com
curl -I https://api.forge.com/v1/health

# Check Python environment
python --version
pip list
which python
```

## 🚨 Common Issues and Solutions

### 1. API Connection Issues

#### Symptoms
- "API connection failed" errors
- "Invalid API key" messages
- Timeout errors
- Rate limiting errors

#### Diagnostic Steps
```bash
# Test API connectivity
python cli.py api test

# Check API key
echo $FORGE_API_KEY

# Test network connectivity
curl -I https://api.forge.com/v1/health

# Check API key validity
python cli.py api validate-key
```

#### Solutions
```bash
# 1. Verify API key
# Check if API key is set correctly
export FORGE_API_KEY="your_actual_api_key"

# 2. Check API key format
# Ensure key is not truncated or malformed
echo $FORGE_API_KEY | wc -c

# 3. Test with curl
curl -H "Authorization: Bearer $FORGE_API_KEY" \
     https://api.forge.com/v1/account

# 4. Check rate limits
python cli.py api status
```

#### Prevention
- Store API keys securely in environment variables
- Monitor API usage and rate limits
- Implement proper error handling and retry logic
- Use API key rotation practices

### 2. Configuration Issues

#### Symptoms
- "Configuration error" messages
- Missing configuration files
- Invalid JSON syntax errors
- Configuration validation failures

#### Diagnostic Steps
```bash
# Validate configuration
python cli.py config validate

# Check configuration files
ls -la configs/
cat configs/config.json

# Check JSON syntax
python -m json.tool configs/config.json

# List all configuration files
find configs/ -name "*.json" -exec echo {} \;
```

#### Solutions
```bash
# 1. Fix JSON syntax errors
# Use a JSON validator or Python's json module
python -c "import json; json.load(open('configs/config.json'))"

# 2. Restore default configuration
cp configs/default.json configs/config.json

# 3. Validate configuration structure
python cli.py config validate --strict

# 4. Check configuration permissions
chmod 644 configs/*.json
```

#### Prevention
- Use configuration validation before deployment
- Implement configuration versioning
- Use configuration templates
- Regular configuration backups

### 3. Image Generation Issues

#### Symptoms
- Image generation failures
- Poor image quality
- Generation timeouts
- Memory errors during generation

#### Diagnostic Steps
```bash
# Test image generation
python cli.py generate test --prompt "test image"

# Check generation parameters
python cli.py generate params

# Monitor memory usage
python cli.py system memory

# Check output directory
ls -la outputs/
du -sh outputs/
```

#### Solutions
```bash
# 1. Adjust generation parameters
python cli.py config set image_generation.max_batch_size 1

# 2. Clear cache
python cli.py cache clear

# 3. Check disk space
df -h outputs/

# 4. Restart with fresh environment
python cli.py system restart
```

#### Prevention
- Monitor system resources during generation
- Implement proper batch size limits
- Use appropriate image quality settings
- Regular cache cleanup

### 4. Wildcard Processing Issues

#### Symptoms
- Wildcard substitution failures
- Infinite recursion errors
- Missing wildcard files
- Invalid wildcard syntax

#### Diagnostic Steps
```bash
# Test wildcard processing
python cli.py wildcards test

# List available wildcards
python cli.py wildcards list

# Validate wildcard files
python cli.py wildcards validate

# Check wildcard cache
python cli.py wildcards cache status
```

#### Solutions
```bash
# 1. Clear wildcard cache
python cli.py wildcards cache clear

# 2. Rebuild wildcard index
python cli.py wildcards rebuild

# 3. Check wildcard file syntax
python cli.py wildcards validate --fix

# 4. Restore default wildcards
python cli.py wildcards restore-defaults
```

#### Prevention
- Validate wildcard files before use
- Implement wildcard depth limits
- Use proper wildcard syntax
- Regular wildcard file maintenance

### 5. Web Dashboard Issues

#### Symptoms
- Dashboard not loading
- Static files not found
- WebSocket connection errors
- Session management issues

#### Diagnostic Steps
```bash
# Test web server
python cli.py web test

# Check web server status
python cli.py web status

# Test static files
curl -I http://localhost:5000/static/css/dashboard.css

# Check web server logs
tail -f logs/web.log
```

#### Solutions
```bash
# 1. Restart web server
python cli.py web restart

# 2. Clear web cache
python cli.py web cache clear

# 3. Check port availability
netstat -tulpn | grep :5000

# 4. Rebuild static files
python cli.py web build-static
```

#### Prevention
- Monitor web server health
- Implement proper error handling
- Use appropriate security headers
- Regular web server maintenance

### 6. Performance Issues

#### Symptoms
- Slow response times
- High memory usage
- CPU spikes
- Timeout errors

#### Diagnostic Steps
```bash
# Monitor performance
python cli.py system performance

# Check resource usage
python cli.py system resources

# Profile application
python cli.py system profile

# Check for memory leaks
python cli.py system memory-leak
```

#### Solutions
```bash
# 1. Optimize configuration
python cli.py config optimize

# 2. Clear caches
python cli.py cache clear all

# 3. Restart application
python cli.py system restart

# 4. Adjust performance settings
python cli.py config set performance.worker_processes 2
```

#### Prevention
- Regular performance monitoring
- Implement caching strategies
- Optimize database queries
- Use appropriate resource limits

### 7. File System Issues

#### Symptoms
- File permission errors
- Disk space issues
- File corruption
- Missing directories

#### Diagnostic Steps
```bash
# Check file system
python cli.py system filesystem

# Check permissions
ls -la outputs/ logs/ cache/

# Check disk space
df -h

# Validate file integrity
python cli.py system validate-files
```

#### Solutions
```bash
# 1. Fix permissions
chmod 755 outputs/ logs/ cache/
chmod 644 outputs/* logs/* cache/*

# 2. Create missing directories
mkdir -p outputs/ logs/ cache/

# 3. Clean up old files
python cli.py system cleanup

# 4. Check file system
fsck /dev/sda1  # Replace with actual device
```

#### Prevention
- Regular file system maintenance
- Implement proper backup procedures
- Monitor disk space usage
- Use appropriate file permissions

### 8. Dependency Issues

#### Symptoms
- Import errors
- Missing modules
- Version conflicts
- Package installation failures

#### Diagnostic Steps
```bash
# Check dependencies
python cli.py system dependencies

# List installed packages
pip list

# Check for conflicts
pip check

# Validate virtual environment
python cli.py system venv
```

#### Solutions
```bash
# 1. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 2. Update dependencies
pip install -r requirements.txt --upgrade

# 3. Fix conflicts
pip install --upgrade pip
pip install -r requirements.txt

# 4. Recreate virtual environment
python -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt
```

#### Prevention
- Use virtual environments
- Pin dependency versions
- Regular dependency updates
- Test dependency changes

## 🔧 Advanced Troubleshooting

### Debug Mode
```bash
# Enable debug mode
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with debug output
python cli.py --debug [command]

# Enable verbose logging
python cli.py --verbose [command]
```

### Profiling
```bash
# Profile application
python -m cProfile -o profile.stats cli.py [command]

# Analyze profile results
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)
"

# Memory profiling
python -m memory_profiler cli.py [command]
```

### Network Diagnostics
```bash
# Test network connectivity
python cli.py network test

# Check DNS resolution
nslookup api.forge.com

# Test HTTP connectivity
curl -v https://api.forge.com/v1/health

# Check firewall rules
iptables -L
```

### System Diagnostics
```bash
# Comprehensive system check
python cli.py system diagnose --full

# Check system requirements
python cli.py system requirements

# Validate installation
python cli.py system validate

# Performance benchmark
python cli.py system benchmark
```

## 🚨 Emergency Procedures

### Critical Issues
```bash
# Emergency stop
python cli.py system stop

# Emergency restart
python cli.py system restart --emergency

# Rollback to previous version
git checkout HEAD~1
python cli.py system restart

# Disable all services
python cli.py system disable
```

### Data Recovery
```bash
# Backup current state
python cli.py backup create

# Restore from backup
python cli.py backup restore [backup_id]

# Recover configuration
python cli.py config restore [config_id]

# Rebuild indexes
python cli.py system rebuild
```

### System Recovery
```bash
# Full system reset
python cli.py system reset --confirm

# Reinstall application
python cli.py system reinstall

# Restore defaults
python cli.py system restore-defaults

# Clean installation
python cli.py system clean-install
```

## 📊 Monitoring and Prevention

### Health Monitoring
```bash
# Set up health checks
python cli.py monitor setup

# Start monitoring
python cli.py monitor start

# Check health status
python cli.py monitor status

# View monitoring logs
tail -f logs/monitor.log
```

### Automated Maintenance
```bash
# Set up automated maintenance
python cli.py maintenance setup

# Run maintenance tasks
python cli.py maintenance run

# Schedule maintenance
python cli.py maintenance schedule

# View maintenance logs
tail -f logs/maintenance.log
```

### Performance Monitoring
```bash
# Start performance monitoring
python cli.py performance monitor

# View performance metrics
python cli.py performance metrics

# Set up alerts
python cli.py performance alerts

# Generate performance report
python cli.py performance report
```

## 📝 Troubleshooting Checklist

### Before Starting
- [ ] Check system requirements
- [ ] Verify installation
- [ ] Check configuration
- [ ] Review recent changes
- [ ] Check system resources

### During Troubleshooting
- [ ] Document the issue
- [ ] Collect relevant logs
- [ ] Test in isolation
- [ ] Try simple solutions first
- [ ] Document solutions

### After Resolution
- [ ] Verify the fix works
- [ ] Update documentation
- [ ] Implement preventive measures
- [ ] Monitor for recurrence
- [ ] Share knowledge with team

## 🎯 Best Practices

### Prevention
- Regular system maintenance
- Monitor system health
- Keep dependencies updated
- Implement proper logging
- Use configuration validation

### Documentation
- Document all issues and solutions
- Maintain troubleshooting guides
- Update procedures regularly
- Share knowledge with team
- Create runbooks for common issues

### Testing
- Test solutions in staging
- Validate fixes thoroughly
- Monitor for side effects
- Implement regression testing
- Use automated testing

This troubleshooting guide provides comprehensive procedures for diagnosing and resolving issues with the Forge-API-Tool. Use it as a reference for common problems and as a foundation for developing project-specific troubleshooting procedures. 