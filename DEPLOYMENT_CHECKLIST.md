# Production Deployment Checklist

## Pre-Deployment

### Security
- [ ] Change default passwords in `backend/auth.py`
- [ ] Generate new SECRET_KEY in `backend/.env`
- [ ] Update CORS allowed origins in `backend/main.py`
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Review and remove test users

### Configuration
- [ ] Set `ACCESS_TOKEN_EXPIRE_MINUTES` appropriately
- [ ] Configure production database (replace fake_users_db)
- [ ] Set up environment variables
- [ ] Configure logging levels
- [ ] Set up monitoring/alerting
- [ ] Configure backup strategy

### Code Review
- [ ] Remove debug print statements
- [ ] Check for hardcoded credentials
- [ ] Verify error handling
- [ ] Review API endpoint security
- [ ] Test all authentication flows
- [ ] Validate input sanitization

### Testing
- [ ] Run system health check: `python system_check.py`
- [ ] Test all user roles (admin, operator)
- [ ] Verify attack detection accuracy
- [ ] Load test with multiple users
- [ ] Test token expiration handling
- [ ] Verify CORS configuration
- [ ] Test on target deployment environment

## Deployment Steps

### Backend Deployment

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Edit .env file
SECRET_KEY=<generate-secure-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. **Run with Production Server**
```bash
# Using Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or using systemd service
sudo systemctl start vanet-backend
```

### Frontend Deployment

1. **Build for Production**
```bash
cd client
npm run build
```

2. **Deploy Static Files**
```bash
# Copy dist/ folder to web server
# Configure nginx/apache to serve files
# Set up reverse proxy to backend
```

3. **Configure Web Server**
```nginx
# nginx example
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        root /var/www/vanet/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Post-Deployment

### Verification
- [ ] Test login functionality
- [ ] Verify API endpoints respond
- [ ] Check attack detection works
- [ ] Test user role permissions
- [ ] Verify token authentication
- [ ] Check HTTPS is working
- [ ] Test from different networks

### Monitoring
- [ ] Set up application monitoring
- [ ] Configure error logging
- [ ] Set up performance monitoring
- [ ] Configure uptime monitoring
- [ ] Set up security alerts
- [ ] Monitor resource usage

### Documentation
- [ ] Update deployment documentation
- [ ] Document server configuration
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures
- [ ] Create user training materials

## Security Hardening

### Backend
- [ ] Disable debug mode
- [ ] Set secure cookie flags
- [ ] Implement request throttling
- [ ] Add IP whitelisting (if needed)
- [ ] Set up WAF (Web Application Firewall)
- [ ] Configure security headers
- [ ] Enable audit logging

### Database
- [ ] Use encrypted connections
- [ ] Implement regular backups
- [ ] Set up access controls
- [ ] Enable query logging
- [ ] Configure retention policies

### Network
- [ ] Configure firewall rules
- [ ] Set up VPN access (if needed)
- [ ] Enable DDoS protection
- [ ] Configure load balancer
- [ ] Set up CDN (if needed)

## Maintenance

### Regular Tasks
- [ ] Review logs weekly
- [ ] Update dependencies monthly
- [ ] Rotate passwords quarterly
- [ ] Review user accounts monthly
- [ ] Test backups monthly
- [ ] Update documentation as needed

### Updates
- [ ] Test updates in staging first
- [ ] Schedule maintenance windows
- [ ] Notify users of downtime
- [ ] Keep rollback plan ready
- [ ] Document changes

## Rollback Plan

### If Deployment Fails
1. Stop new services
2. Restore previous version
3. Verify functionality
4. Investigate issues
5. Document problems
6. Plan fixes

### Backup Locations
- Code: Git repository
- Database: Backup server
- Configuration: Version control
- Logs: Archive storage

## Support

### Contact Information
- Technical Lead: [email]
- DevOps Team: [email]
- Security Team: [email]

### Resources
- Documentation: /docs
- API Docs: /api/docs
- Monitoring: [monitoring-url]
- Logs: [logging-url]

## Compliance

### Data Protection
- [ ] GDPR compliance (if applicable)
- [ ] Data encryption at rest
- [ ] Data encryption in transit
- [ ] User data retention policy
- [ ] Privacy policy updated

### Audit
- [ ] Security audit completed
- [ ] Penetration testing done
- [ ] Code review completed
- [ ] Compliance check passed

---

**Deployment Date**: ___________
**Deployed By**: ___________
**Version**: 3.0.0
**Status**: ___________

---

## Quick Commands

### Check System Status
```bash
python system_check.py
```

### View Backend Logs
```bash
tail -f /var/log/vanet/backend.log
```

### Restart Services
```bash
sudo systemctl restart vanet-backend
sudo systemctl restart nginx
```

### Check Service Status
```bash
sudo systemctl status vanet-backend
sudo systemctl status nginx
```

### Database Backup
```bash
# Add your backup command
```

---

**Remember**: Always test in staging before production!
