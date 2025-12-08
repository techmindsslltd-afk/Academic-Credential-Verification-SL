#  Academic Credential Verification System (ACV-SL)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0.3-green.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

> **Blockchain-Powered Academic Credential Verification Platform** - A comprehensive system for issuing, verifying, and managing academic credentials with blockchain security and IPFS backup.

## 🎯 Overview

CertChain is a dual-verification platform for academic credentials that combines blockchain security for partner institutions with global accreditation lookup capabilities. The system enables universities to issue tamper-proof credentials, employers to verify credentials instantly, and students to share their achievements securely.

### Key Features

- 🔐 **Blockchain Security** - Credentials are cryptographically hashed and stored on an immutable distributed ledger
- 🌐 **IPFS Backup** - Decentralized storage for credential documents and metadata
- 🏛️ **Institution Management** - Partner and non-partner institution support with accreditation tracking
- 👥 **Multi-Role System** - Separate dashboards for Students, Institution Admins, Employers, and Super Admins
- ✅ **Instant Verification** - Verify credentials by ID or blockchain hash with real-time status checking
- 📱 **QR Code Generation** - Shareable QR codes for easy credential verification
- 📄 **Document Upload** - Support for certificate file uploads with hash verification
- 🔍 **Accreditation Lookup** - Global university accreditation status verification
- 📊 **Analytics Dashboard** - Comprehensive reporting and activity tracking
- 🌍 **Multi-language Support** - Support for multiple languages (English, Krio, French, Spanish, etc.)

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/techmindsslltd-afk/Academic-Credential-Verification-SL.git
   cd Academic-Credential-Verification-SL
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your configuration:
   # - SECRET_KEY
   # - Database credentials
   # - Email settings
   # - Allowed hosts
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser** (optional)
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:8000/`

## 📁 Project Structure

```
CertChain/
│
├── apps/
│   ├── accounts/          # User authentication and profile management
│   ├── credentials/       # Credential issuance and verification
│   ├── institutions/      # Institution management and accreditation
│   ├── verifications/     # Verification logs and tracking
│   ├── accreditation/     # Accreditation status management
│   ├── home/              # Main views and public pages
│   ├── static/             # Static files (CSS, JS, images)
│   └── templates/          # HTML templates
│
├── core/                   # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
│
├── media/                  # User-uploaded files (excluded from git)
├── staticfiles/            # Collected static files (excluded from git)
├── requirements.txt        # Python dependencies
├── manage.py               # Django management script
└── README.md               # This file
```

## 🔑 User Roles

### Student
- View issued credentials
- Share credentials with employers
- Download credential documents
- View verification history

### Institution Admin
- Issue new credentials
- Manage student credentials
- Upload certificate documents
- View institution statistics
- Revoke credentials if needed

### Employer
- Verify credentials by ID or hash
- View credential details and status
- Check institution accreditation
- Track verification history
- Monthly verification limits

### Super Admin
- Full system access
- Manage all users and institutions
- System configuration
- Analytics and reporting

## 🔐 Security Features

- **CSRF Protection** - All forms protected against cross-site request forgery
- **Session Security** - Secure session management with timeout
- **Password Hashing** - Bcrypt password hashing
- **Blockchain Hashing** - SHA-256 hashing for credential integrity
- **Document Verification** - File hash verification for uploaded certificates
- **Role-Based Access Control** - Granular permissions per user role

## 🌐 API Endpoints

### Public Endpoints
- `GET /api/v1/institutions/` - List institutions (with filtering)
- `POST /api/v1/credentials/verify/` - Verify a credential
- `GET /credentials/verify/<credential_id>/` - Public verification page

### Authenticated Endpoints
- `GET /api/v1/credentials/` - List credentials (role-based)
- `POST /api/v1/credentials/issue/` - Issue new credential
- `PUT /api/v1/credentials/<id>/` - Update credential
- `POST /api/v1/credentials/<id>/revoke/` - Revoke credential

## 🛠️ Technology Stack

- **Backend**: Django 5.0.3
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS)
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: Django REST Framework
- **Authentication**: JWT + Session Authentication
- **Blockchain**: SHA-256 hashing (ready for blockchain integration)
- **Storage**: IPFS-ready (for decentralized storage)

## 📦 Dependencies

Key dependencies include:
- Django 5.0.3
- Django REST Framework
- django-filter
- python-decouple (for environment variables)
- Pillow (for image processing)
- And more... (see `requirements.txt`)

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up environment variables
- [ ] Configure static file serving
- [ ] Set up SSL/HTTPS
- [ ] Configure email backend
- [ ] Set up backup system
- [ ] Configure logging
- [ ] Set up monitoring

### Docker Deployment

```bash
docker-compose up -d
```

## 🤝 Contributing

This is a proprietary project by TechMinds SL Ltd. For contributions or inquiries, please contact the development team.

## 📄 License

Copyright (c) 2024 - present TechMinds SL Ltd

All rights reserved. This software is proprietary and confidential.

## 📞 Support

For support, issues, or questions:
- **Organization**: TechMinds SL Ltd
- **Repository**: [Academic-Credential-Verification-SL](https://github.com/techmindsslltd-afk/Academic-Credential-Verification-SL)

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 🙏 Acknowledgments

- Built with Django and Django REST Framework
- UI components inspired by Material Design principles
- Blockchain concepts implemented for credential security

---

**Made with ❤️ by TechMinds SL Ltd**
