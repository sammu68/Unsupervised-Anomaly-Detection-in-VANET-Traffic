# Installation Guide - VANET System v3.0

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- pip (Python package manager)
- npm (Node package manager)

## Quick Installation (Windows)

Simply double-click `run_project.bat` - it will automatically:
1. Check for Python and Node.js
2. Install all dependencies
3. Start both backend and frontend
4. Open your browser to the dashboard

## Manual Installation

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# This will install:
# - fastapi==0.109.0
# - uvicorn[standard]==0.27.0
# - tensorflow==2.15.0
# - numpy==1.26.3
# - pandas==2.1.4
# - python-multipart==0.0.6
# - python-jose[cryptography]==3.3.0  (NEW - JWT handling)
# - passlib[bcrypt]==1.7.4            (NEW - Password hashing)
# - python-dotenv==1.0.0              (NEW - Environment variables)
```

### Step 2: Configure Environment (Optional)

The system comes with default settings in `backend/.env`:

```env
SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**For Production**: Generate a secure secret key:
```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Using OpenSSL
openssl rand -hex 32
```

Then update the `SECRET_KEY` in `.env` file.

### Step 3: Frontend Setup

```bash
# Navigate to client directory
cd client

# Install Node dependencies
npm install

# This will install all dependencies from package.json
# No new dependencies added in v3.0 - uses existing React, Framer Motion, Recharts
```

### Step 4: Start the Application

#### Option A: Start Both Services Separately

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd client
npm run dev
```

#### Option B: Use the Batch File (Windows)
```bash
# From project root
run_project.bat
```

### Step 5: Access the Application

1. Open your browser to: http://localhost:5173
2. Login with default credentials:
   - Admin: `admin` / `admin123`
   - Operator: `operator` / `operator123`

## Verification

### Check Backend
```bash
# Test if backend is running
curl http://localhost:8000/

# Expected response:
{
  "service": "VANET Anomaly Detection API",
  "version": "3.0.0",
  "model_loaded": true,
  "threshold": 0.1114,
  "features": ["JWT Authentication", "Attack Classification", "Role-based Access"]
}
```

### Check Authentication
```bash
# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Expected response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "role": "admin",
    "full_name": "System Administrator"
  }
}
```

### Check Frontend
- Navigate to http://localhost:5173
- You should see the login screen
- Enter credentials and verify you can access the dashboard

## Troubleshooting

### Backend Issues

#### ImportError: No module named 'jose'
```bash
pip install python-jose[cryptography]
```

#### ImportError: No module named 'passlib'
```bash
pip install passlib[bcrypt]
```

#### TensorFlow Issues
```bash
# If TensorFlow fails to install, try:
pip install tensorflow==2.15.0 --no-cache-dir

# For Apple Silicon Macs:
pip install tensorflow-macos==2.15.0
pip install tensorflow-metal==1.1.0
```

#### Port Already in Use
```bash
# Change backend port
python -m uvicorn main:app --reload --port 8001

# Update frontend API_URL in client/src/hooks/useTrafficData.js
const API_URL = "http://localhost:8001";
```

### Frontend Issues

#### npm install fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### Port 5173 already in use
```bash
# Vite will automatically try the next available port
# Or specify a different port:
npm run dev -- --port 3000
```

### Authentication Issues

#### "Could not validate credentials"
- Check if backend is running
- Verify token hasn't expired (default: 30 minutes)
- Clear browser localStorage and login again
- Check browser console for errors

#### "Admin privileges required"
- Ensure you're logged in as admin user
- Operator role has read-only access
- Some endpoints require admin role

## Database Setup (Optional - Future Enhancement)

Currently, the system uses an in-memory user database. For production:

1. Install database driver (e.g., PostgreSQL):
```bash
pip install psycopg2-binary sqlalchemy
```

2. Update `backend/auth.py` to use real database
3. Create user management endpoints
4. Implement user registration

## Production Deployment

### Backend (FastAPI)

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (React)

```bash
# Build for production
cd client
npm run build

# Serve with nginx or any static file server
# Build output is in client/dist/
```

### Environment Variables (Production)

Create a production `.env` file:

```env
# Generate secure key
SECRET_KEY=<use-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (if using)
DATABASE_URL=postgresql://user:password@localhost/vanet_db

# CORS
ALLOWED_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
```

### Security Checklist

- [ ] Change default passwords
- [ ] Generate new SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring/logging
- [ ] Regular security updates
- [ ] Backup strategy

## Docker Deployment (Optional)

Create `Dockerfile` for backend:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./backend:/app

  frontend:
    build: ./client
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

Run with:
```bash
docker-compose up
```

## System Requirements

### Minimum
- CPU: 2 cores
- RAM: 4 GB
- Storage: 2 GB
- OS: Windows 10, macOS 10.15, Ubuntu 20.04

### Recommended
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 5 GB
- OS: Windows 11, macOS 12+, Ubuntu 22.04
- GPU: Optional (for faster TensorFlow inference)

## Support

If you encounter issues:

1. Check this installation guide
2. Review error messages in terminal
3. Check browser console (F12)
4. Verify all dependencies are installed
5. Ensure ports 8000 and 5173 are available
6. Check firewall settings

## Next Steps

After installation:

1. Read `IMPROVEMENTS.md` for feature documentation
2. Explore API docs at http://localhost:8000/docs
3. Test attack classification by toggling attack mode
4. Review attack panel for threat details
5. Customize user credentials for production

---

**Installation Complete!** 🎉

You're now ready to use the VANET Anomaly Detection System v3.0.
