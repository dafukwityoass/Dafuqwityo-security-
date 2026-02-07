# Production Deployment Guide
## Paymentus Holdings Inc. Clone - Financial Services Platform

This guide provides comprehensive instructions for deploying the production-ready Paymentus financial services platform with enhanced security, compliance, and banking integrations.

---

## 🏗 Architecture Overview

### Core Components
- **Frontend**: React application with real-time payment processing
- **Backend**: FastAPI with comprehensive financial infrastructure
- **Database**: MongoDB with encryption and audit trails
- **Payment Processing**: Stripe integration with compliance monitoring
- **Banking APIs**: Plaid integration templates for account linking
- **Security**: Multi-layer encryption and authentication
- **Compliance**: KYC/AML monitoring and regulatory reporting

### Enhanced Security Features
- **Multi-signature Bitcoin wallets** with hardware security module support
- **End-to-end encryption** for all sensitive financial data
- **Real-time AML/OFAC screening** for transactions
- **Comprehensive audit trails** with cryptographic integrity
- **Zero-trust security architecture** with role-based access control

---

## 📋 Pre-Deployment Requirements

### 1. Legal and Regulatory
- [ ] **Money Services Business (MSB) Registration** with FinCEN
- [ ] **State money transmitter licenses** in operational jurisdictions
- [ ] **Banking partnership agreements** for ACH processing
- [ ] **Legal counsel review** of all compliance implementations
- [ ] **Regulatory approval** for cryptocurrency handling (if applicable)

### 2. API Keys and Credentials
```env
# Required Production Environment Variables
STRIPE_SECRET_KEY=sk_live_...          # Production Stripe key
PLAID_CLIENT_ID=your_plaid_client_id   # Production Plaid credentials  
PLAID_SECRET=your_plaid_secret         # Production Plaid secret
PLAID_ENV=production                   # Production environment
JWT_SECRET_KEY=your_256_bit_secret     # Cryptographically secure JWT secret
OFAC_API_KEY=your_ofac_api_key        # OFAC sanctions screening API
MONGO_ROOT_USER=secure_username        # MongoDB root credentials
MONGO_ROOT_PASSWORD=secure_password    # Strong password for MongoDB
```

### 3. Infrastructure Requirements
- **Minimum 3 application servers** for high availability
- **MongoDB replica set** with automatic failover
- **Redis cluster** for session management and caching
- **Load balancer** with SSL termination
- **Monitoring stack** (Prometheus, Grafana, ELK)

---

## 🔐 Security Implementation

### 1. Encryption Setup
```bash
# Generate encryption keys for sensitive data
cd /app/backend
python -c "
from cryptography.fernet import Fernet
import os
key = Fernet.generate_key()
with open('.encryption_key', 'wb') as f:
    f.write(key)
os.chmod('.encryption_key', 0o600)
print('Encryption key generated successfully')
"
```

### 2. Digital Signing Keys
```bash
# Generate RSA key pair for digital signatures
openssl genpkey -algorithm RSA -out .rsa_private_key.pem -pkcs8 -aes256
chmod 600 .rsa_private_key.pem
```

### 3. SSL/TLS Configuration
```nginx
# /deployment/nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    location /api {
        proxy_pass http://paymentus-api:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        proxy_pass http://paymentus-frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🚀 Deployment Steps

### 1. Environment Setup
```bash
# Clone repository and navigate to deployment directory
git clone <repository-url>
cd paymentus-clone/deployment

# Create production environment file
cp .env.template .env.production
# Edit .env.production with your production values

# Create required directories
mkdir -p logs nginx/ssl grafana/dashboards prometheus backup/scripts
```

### 2. Database Initialization
```bash
# Initialize MongoDB replica set
docker-compose -f docker-compose.production.yml up -d mongo
sleep 30

# Initialize replica set
docker exec mongo mongo --eval "
rs.initiate({
  _id: 'rs0',
  members: [{_id: 0, host: 'mongo:27017'}]
})
"

# Create application database and users
docker exec mongo mongo paymentus_production --eval "
db.createUser({
  user: 'paymentus_app',
  pwd: 'secure_app_password',
  roles: [{role: 'readWrite', db: 'paymentus_production'}]
})
"
```

### 3. Application Deployment
```bash
# Build and deploy all services
docker-compose -f docker-compose.production.yml up -d

# Verify all services are running
docker-compose -f docker-compose.production.yml ps

# Check application health
curl -f http://localhost:8001/api/health
```

### 4. SSL Certificate Setup
```bash
# Using Let's Encrypt (recommended)
certbot certonly --webroot -w /var/www/html -d your-domain.com

# Copy certificates to nginx directory
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/

# Restart nginx to load certificates
docker-compose -f docker-compose.production.yml restart nginx
```

---

## 📊 Monitoring and Observability

### 1. Prometheus Configuration
```yaml
# /deployment/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'paymentus-api'
    static_configs:
      - targets: ['paymentus-api:8001']
    metrics_path: '/api/metrics'
    
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongo:9216']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
```

### 2. Grafana Dashboards
- **Financial Transactions Dashboard**: Real-time transaction monitoring
- **Compliance Monitoring Dashboard**: AML/KYC metrics and alerts
- **System Performance Dashboard**: Infrastructure health metrics
- **Security Dashboard**: Authentication and threat detection metrics

### 3. Alerting Rules
```yaml
# Critical alerts for financial operations
groups:
  - name: financial_alerts
    rules:
      - alert: HighTransactionFailureRate
        expr: rate(transaction_failures_total[5m]) > 0.1
        labels:
          severity: critical
        annotations:
          summary: "High transaction failure rate detected"
          
      - alert: ComplianceSystemDown
        expr: up{job="compliance-monitor"} == 0
        labels:
          severity: critical
        annotations:
          summary: "Compliance monitoring system is down"
```

---

## 🛡 Compliance and Audit

### 1. Daily Compliance Checks
```bash
# Automated daily compliance verification
#!/bin/bash
# /deployment/scripts/daily_compliance_check.sh

# Check OFAC sanctions list updates
curl -f "https://api.compliance-system.com/ofac/updates" \
  -H "Authorization: Bearer $OFAC_API_KEY"

# Verify encryption key rotation schedule  
python /app/backend/scripts/check_key_rotation.py

# Generate compliance metrics report
python /app/backend/scripts/generate_compliance_report.py --date=$(date +%Y-%m-%d)

# Check for suspicious transaction patterns
python /app/backend/scripts/aml_pattern_analysis.py --lookback=24h
```

### 2. Audit Trail Verification
```python
# Verify audit trail integrity
from financial_infrastructure import AuditLogger

audit_logger = AuditLogger()
integrity_result = await audit_logger.verify_audit_integrity(
    start_date=datetime.now() - timedelta(days=1),
    end_date=datetime.now()
)

if not integrity_result.is_valid:
    # Alert compliance team
    send_alert("Audit trail integrity violation detected")
```

### 3. Regulatory Reporting
```bash
# Automated regulatory report generation
# Run monthly on the 1st of each month
0 0 1 * * python /app/backend/scripts/generate_monthly_reports.py \
  --report-types=CTR,SAR,AML_SUMMARY \
  --output-dir=/backup/regulatory_reports/$(date +%Y-%m)
```

---

## 🔄 Backup and Recovery

### 1. Database Backup Strategy
```bash
# Automated MongoDB backup script
#!/bin/bash
# /deployment/scripts/backup.sh

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mongodb/$BACKUP_DATE"

# Create encrypted backup
mongodump --host mongo:27017 \
  --username $MONGO_ROOT_USER \
  --password $MONGO_ROOT_PASSWORD \
  --authenticationDatabase admin \
  --out $BACKUP_DIR

# Encrypt backup directory
tar -czf ${BACKUP_DIR}.tar.gz -C /backup/mongodb $BACKUP_DATE
openssl enc -aes-256-cbc -salt -in ${BACKUP_DIR}.tar.gz \
  -out ${BACKUP_DIR}.tar.gz.enc -k $BACKUP_ENCRYPTION_KEY

# Upload to secure cloud storage
aws s3 cp ${BACKUP_DIR}.tar.gz.enc \
  s3://paymentus-backups/mongodb/ \
  --server-side-encryption AES256

# Cleanup local files (keep last 7 days)
find /backup/mongodb -name "*.tar.gz.enc" -mtime +7 -delete
```

### 2. Disaster Recovery Testing
```bash
# Quarterly disaster recovery test
#!/bin/bash
# /deployment/scripts/dr_test.sh

# Test database restoration
mongorestore --host mongo-dr:27017 \
  --username $MONGO_ROOT_USER \
  --password $MONGO_ROOT_PASSWORD \
  --authenticationDatabase admin \
  /backup/mongodb/latest/

# Test application connectivity
curl -f http://dr-environment:8001/api/health

# Verify financial data integrity
python /app/backend/scripts/verify_financial_data_integrity.py \
  --environment=disaster_recovery
```

---

## 🧪 Testing and Validation

### 1. Security Testing
```bash
# Automated security testing pipeline
# Run before each deployment

# SAST (Static Application Security Testing)
bandit -r /app/backend -f json -o security_report.json

# DAST (Dynamic Application Security Testing)  
zap-baseline.py -t http://localhost:8001 -J dast_report.json

# Dependency vulnerability scanning
safety check --json --output vulnerability_report.json

# Infrastructure security scanning
docker-bench-security
```

### 2. Compliance Testing
```python
# Automated compliance validation tests
import pytest
from financial_infrastructure import ComplianceMonitor

class TestCompliance:
    @pytest.mark.asyncio
    async def test_aml_screening(self):
        """Test AML screening functionality"""
        compliance = ComplianceMonitor()
        
        # Test high-risk transaction detection
        high_risk_txn = create_high_risk_transaction()
        result = await compliance.monitor_transaction(high_risk_txn)
        
        assert result["requires_review"] == True
        assert "SAR_THRESHOLD" in result["flags"]
    
    @pytest.mark.asyncio  
    async def test_ofac_screening(self):
        """Test OFAC sanctions screening"""
        # Test against known sanctioned entity
        sanctioned_entity = create_test_sanctioned_entity()
        result = await compliance._check_ofac_sanctions(sanctioned_entity.user_id)
        
        assert result["is_sanctioned"] == True
```

### 3. Performance Testing
```bash
# Load testing for production readiness
# Test concurrent user capacity

# API load testing
artillery run /deployment/tests/api_load_test.yml

# Database performance testing  
sysbench --test=oltp --mysql-host=mongo --mysql-user=root run

# Payment processing stress testing
python /deployment/tests/payment_stress_test.py \
  --concurrent-users=1000 \
  --test-duration=300s
```

---

## 📈 Scaling and Optimization

### 1. Horizontal Scaling Configuration
```yaml
# Kubernetes deployment for auto-scaling
apiVersion: apps/v1
kind: Deployment
metadata:
  name: paymentus-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: paymentus-api
  template:
    metadata:
      labels:
        app: paymentus-api
    spec:
      containers:
      - name: api
        image: paymentus/api:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: paymentus-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: paymentus-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Database Optimization
```javascript
// MongoDB performance optimization indexes
// Run in production MongoDB

// User authentication optimization
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "id": 1 }, { unique: true })

// Transaction processing optimization  
db.transactions.createIndex({ 
  "user_id": 1, 
  "timestamp": -1 
})
db.transactions.createIndex({ 
  "status": 1, 
  "timestamp": -1 
})

// Compliance and audit optimization
db.enhanced_transactions.createIndex({
  "risk_score": -1,
  "timestamp": -1
})
db.kyc_documents.createIndex({
  "user_id": 1,
  "verification_status": 1
})

// Payment processing optimization
db.payment_transactions.createIndex({
  "stripe_session_id": 1
}, { unique: true })
db.payment_transactions.createIndex({
  "user_id": 1,
  "payment_status": 1,
  "created_at": -1
})
```

---

## 🚨 Incident Response

### 1. Incident Classification
- **P0 - Critical**: Payment processing down, security breach, compliance violation
- **P1 - High**: Performance degradation, partial service outage
- **P2 - Medium**: Minor feature issues, non-critical bugs
- **P3 - Low**: Enhancement requests, documentation updates

### 2. Automated Incident Response
```python
# Automated incident response system
class IncidentResponse:
    async def handle_critical_incident(self, incident_type, details):
        if incident_type == "security_breach":
            # Immediate containment
            await self.isolate_affected_systems()
            await self.revoke_active_sessions()
            await self.enable_emergency_monitoring()
            
            # Notification
            await self.notify_incident_team()
            await self.notify_legal_counsel()
            await self.prepare_regulatory_notification()
            
        elif incident_type == "compliance_violation":
            # Compliance-specific response
            await self.freeze_affected_accounts()
            await self.generate_incident_report()
            await self.notify_compliance_officer()
```

### 3. Recovery Procedures
```bash
# Emergency recovery runbook
#!/bin/bash
# /deployment/scripts/emergency_recovery.sh

echo "=== EMERGENCY RECOVERY PROCEDURE ==="
echo "Incident ID: $1"
echo "Recovery Type: $2"

case $2 in
  "database_corruption")
    echo "Initiating database recovery..."
    # Stop application servers
    docker-compose -f docker-compose.production.yml stop paymentus-api
    
    # Restore from latest backup
    ./restore_database.sh --backup-date=$(date -d "yesterday" +%Y%m%d)
    
    # Verify data integrity
    python /app/backend/scripts/verify_data_integrity.py
    
    # Restart services
    docker-compose -f docker-compose.production.yml up -d
    ;;
    
  "security_breach")
    echo "Initiating security lockdown..."
    # Revoke all API keys
    python /app/backend/scripts/revoke_all_api_keys.py
    
    # Enable emergency access only
    python /app/backend/scripts/enable_emergency_mode.py
    
    # Generate forensic data
    python /app/backend/scripts/collect_forensic_data.py --incident=$1
    ;;
esac
```

---

## 📝 Maintenance and Updates

### 1. Regular Maintenance Schedule
- **Daily**: Compliance checks, backup verification, security monitoring
- **Weekly**: Performance review, capacity planning, security updates
- **Monthly**: Full system backup test, compliance reporting, security audit
- **Quarterly**: Disaster recovery test, penetration testing, business continuity review

### 2. Update Procedures
```bash
# Zero-downtime deployment procedure
#!/bin/bash
# /deployment/scripts/rolling_update.sh

# Build new application images
docker build -t paymentus/api:$NEW_VERSION ../backend/
docker build -t paymentus/frontend:$NEW_VERSION ../frontend/

# Rolling update with health checks
for i in {1..3}; do
  echo "Updating instance $i..."
  
  # Update single instance
  docker-compose -f docker-compose.production.yml \
    up -d --scale paymentus-api=3 \
    --no-recreate paymentus-api
    
  # Health check
  sleep 30
  curl -f http://localhost:8001/api/health || exit 1
  
  echo "Instance $i updated successfully"
done

echo "Rolling update completed"
```

---

## 📞 Support and Maintenance

### Technical Support Contacts
- **DevOps Team**: devops@paymentus.com (Infrastructure, Deployment)
- **Security Team**: security@paymentus.com (Security Incidents, Compliance)
- **Compliance Officer**: compliance@paymentus.com (Regulatory Issues)
- **Legal Counsel**: legal@paymentus.com (Regulatory Guidance)

### Emergency Escalation
1. **On-call Engineer** (24/7): +1-555-EMERGENCY
2. **Security Team Lead**: +1-555-SECURITY
3. **CTO**: +1-555-EXECUTIVE
4. **Legal Counsel**: +1-555-LEGAL-911

### Monitoring and Alerting
- **Grafana Dashboards**: https://monitoring.paymentus.com
- **Log Aggregation**: https://logs.paymentus.com  
- **Uptime Monitoring**: https://status.paymentus.com
- **Security Dashboard**: https://security.paymentus.com

---

## ✅ Production Readiness Checklist

### Security
- [ ] All encryption keys properly generated and secured
- [ ] SSL/TLS certificates installed and configured
- [ ] Multi-factor authentication enabled for all admin accounts
- [ ] Security headers configured in web server
- [ ] Rate limiting implemented and tested
- [ ] Penetration testing completed and issues resolved

### Compliance
- [ ] MSB registration completed with FinCEN
- [ ] State licenses obtained for all operational jurisdictions
- [ ] KYC/AML procedures documented and implemented
- [ ] OFAC screening integrated and tested
- [ ] Audit trails verified and tamper-evident
- [ ] Compliance officer appointed and trained

### Infrastructure
- [ ] High availability configuration tested
- [ ] Load balancing configured and tested
- [ ] Database replication setup and verified
- [ ] Backup and recovery procedures tested
- [ ] Monitoring and alerting configured
- [ ] Disaster recovery plan documented and tested

### Application
- [ ] All tests passing (unit, integration, security, compliance)
- [ ] Performance benchmarks met
- [ ] Error handling and logging comprehensive
- [ ] API documentation complete and accurate
- [ ] User acceptance testing completed
- [ ] Rollback procedures documented and tested

### Legal and Regulatory
- [ ] Legal counsel review completed
- [ ] Regulatory approvals obtained
- [ ] Privacy policies updated and published  
- [ ] Terms of service reviewed and finalized
- [ ] Insurance coverage in place
- [ ] Incident response plan legal review completed

---

## 🔗 Additional Resources

### Documentation
- [Financial Infrastructure API Documentation](./financial_infrastructure.py)
- [Security Configuration Guide](./security-config.yml)
- [Regulatory Compliance Implementation](./regulatory-compliance.md)
- [Docker Deployment Configuration](./docker-compose.production.yml)

### External References
- [FinCEN MSB Registration Guide](https://www.fincen.gov/money-services-business-msb-registration)
- [Plaid API Documentation](https://plaid.com/docs/)
- [Stripe Connect Documentation](https://stripe.com/docs/connect)
- [PCI DSS Requirements](https://www.pcisecuritystandards.org/)
- [GDPR Compliance Guide](https://gdpr.eu/)

### Compliance Resources
- [Federal Financial Institutions Examination Council (FFIEC)](https://www.ffiec.gov/)
- [Conference of State Bank Supervisors (CSBS)](https://www.csbs.org/)
- [Financial Crimes Enforcement Network (FinCEN)](https://www.fincen.gov/)
- [Office of Foreign Assets Control (OFAC)](https://www.treasury.gov/about/organizational-structure/offices/Pages/Office-of-Foreign-Assets-Control.aspx)

---

**⚖️ Legal Disclaimer**: This deployment guide is provided for technical reference only. All financial services operations require proper legal and regulatory approval. Consult with qualified legal and compliance professionals before deploying to production.