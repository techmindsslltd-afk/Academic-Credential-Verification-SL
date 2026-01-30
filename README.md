# 🎓 ACV-SL — Academic Credential Verification Platform

ACV-SL is a **role-based** academic credential issuance and verification platform that combines **privacy-preserving student identity**, **government accreditation workflows**, and **blockchain-style attestations** to make credential verification fast, trustworthy, and auditable.

---

## 🚀 Key Features

### 🏛️ Universities / Institutions
- **Institution profiles**: Register and manage institutional information.
- **Issue digital credentials**: Create and manage digital certificates for students.
- **Blockchain attestations**: Record on-chain proof (tx hash + block number) for tamper-evident validation.
- **Institution stats**: Track student records, issuance status, and attestation counts.

### 🎓 Students
- **My Credentials Wallet**: View issued credentials with institution, program, grade, and issue date.
- **🛡️ Privacy ID**: NIN-based privacy protection using **HMAC-SHA256 hashed NIN** (no raw identifiers stored).
- **🔗 Blockchain Identity**: A deterministic **Solana-style address** generated from your privacy ID.
- **✅ On-chain Proof**: View **Confirmed/Pending** status, **Transaction Hash**, and **Block Number** for every credential.
- **⚖️ Accreditation**: Request official government review for your issued credentials.

### 🏛️ Government Entities
- **Government Dashboard**: High-level metrics for accreditation requests and system health.
- **Accreditation Workflow**: Review, approve, or reject institutional credential requests.
- **Audit Trails**: Full transparency on status changes and attestation links.

### 🔍 Employers / Verifiers
- **Instant Verification**: Search by **Credential ID**, **QR Code**, or **Blockchain Hash**.
- **Detailed Reports**: View a structured table of academic details and blockchain proof fields.
- **Audit Logs**: Every verification attempt is logged for security and analytics.

### 🛡️ Super Admin
- **System Ledger**: Unified view of all blockchain attestations and transaction states.
- **Analytics**: Deep insights into user growth, institution activity, and verification volume.

---

## 🛠️ Tech Stack

- **Backend**: Python / Django 5 + Django REST Framework (DRF)
- **Database**: **MySQL** (optimized with custom UUID compatibility)
- **Frontend**: Django Templates + Vanilla JavaScript + Modern CSS
- **Blockchain**: Solana-inspired attestation patterns & transaction tracking
- **Security**: BruteBuster (Brute force protection), JWT, & Session Security
- **Deployment**: Docker, Gunicorn, & Nginx

---

## 📂 Project Structure

- `core/` — Project configuration, security settings, and custom DB fields.
- `apps/accounts/` — User management, RBAC, and Privacy Profiles.
- `apps/credentials/` — Issuance logic and Blockchain service integration.
- `apps/verifications/` — Public & private verification APIs.
- `apps/home/` — Role-specific dashboards and analytics.
- `apps/static/` — Frontend assets (CSS/JS/Images).

---

## 💻 Local Setup (Windows)

### 1️⃣ Environment Setup
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Configure MySQL
Create a database named `ACV-SL`. Update `core/settings.py` if your credentials differ:
- **DB Name**: `ACV-SL`
- **User**: `root`
- **Password**: `(empty)`

### 3️⃣ Initialize Database
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4️⃣ Run Development Server
```powershell
python manage.py runserver
```
Visit: `http://127.0.0.1:8000/dashboard`

---

## 📡 API Quick Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/auth/` | `POST` | User login & token acquisition |
| `/api/v1/verifications/verify/` | `POST` | Verify by ID, TX, or Hash |
| `/api/v1/credentials/` | `GET` | List/Detail credentials |
| `/api/v1/accreditation/` | `POST` | Handle Gov accreditation |

---

## ⛓️ Blockchain Attestations

The system simulates/interfaces with on-chain attestations. To backfill existing data:
```powershell
python manage.py backfill_attestations --limit 100
```

---

## 🐋 Docker Support
```bash
docker-compose up --build
```

---

## ⚠️ Troubleshooting

- **MySQL UUID Errors**: Ensure you are using the custom `MySQLCompatibleUUIDField`.
- **Styling Issues**: Use **Ctrl + F5** to clear cache (the project uses `?v=` versioning).
- **Missing NIN Salt**: Set `NIN_SALT` in your `.env` for secure identity hashing.

---

## 📄 License
Copyright © 2024 TechMinds SL Ltd. All rights reserved.
