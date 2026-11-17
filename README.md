# HOMETRACE (PWA)
### Design and Implementation of a Progressive Web Application for Real Estate Property Listing, Search and Transactions in Nigeria

---

## 1. Project Introduction

**Hometrace** is a production-grade Progressive Web Application (PWA) designed to transform and modernize the Nigerian real estate ecosystem. By providing a centralized, transparent, and verified marketplace, Hometrace connects property agents with prospective buyers and tenants across all 36 Nigerian states and the Federal Capital Territory (Abuja).

Built strictly using **Django**, **PostgreSQL** (with zero-setup SQLite development fallback), **Tailwind CSS**, and **Vanilla JavaScript**, Hometrace delivers an installable, mobile-first experience with offline caching, role-based access control, in-app messaging, Paystack payment processing, and comprehensive platform governance.

---

## 2. Problem Statement

Traditional property acquisition in Nigeria faces severe structural challenges:
- **Fragmented and Unreliable Information**: Ghost listings, outdated property statuses, and manipulated pricing.
- **High Friction and Stress**: Exhausting physical scouting under tropical weather and gridlock traffic.
- **Unverified Middlemen & Scam Agents**: Pervasive agent touts misrepresenting properties and collecting unauthorized search fees.
- **Inadequate Search Mechanisms**: Existing classified sites lack filters for vital Nigerian infrastructure (standby generators, borehole water, uniformed security, solar inverters).
- **Poor Communication & Insecure Payments**: Lack of integrated, traceable communication and digital payment records.

Hometrace resolves these challenges through verified agent credential auditing, mandatory listing moderation, infrastructure-specific search faceting, live in-app chat, and Paystack digital verification.

---

## 3. Main Objectives

1. **Centralized Discovery**: Maintain an aggregated, verified repository of residential and commercial properties in Nigeria.
2. **Multi-Faceted Search Engine**: Enable simultaneous multi-parameter filtering by Nigerian states, cities, neighbourhoods, budget ranges, and essential amenities (PHCN, generator, borehole, security).
3. **Direct Agent-Buyer Communication**: Provide internal conversation threads with unread indicators and live polling.
4. **Paystack Payment Integration**: Seamlessly handle inspection booking deposits, agent credential verification fees, and featured listing promotions.
5. **Progressive Web Application (PWA)**: Ensure fast loading, home screen installability on Android/iOS/Desktop, and offline shell caching.
6. **Triple-Role Governance**: Distinct, protected portals for Property Agents, Buyers/Renters, and Platform Administrators.

---

## 4. Technology Stack

- **Backend Framework**: Python 3.12, Django 6.0
- **Database**: PostgreSQL (configured via `DATABASE_URL` in `.env`) with seamless SQLite development fallback
- **Frontend Architecture**: Semantic HTML5, Django Server-Rendered Templates, Vanilla JavaScript
- **Styling & Design System**: Tailwind CSS, Google Fonts (*Plus Jakarta Sans*), custom CSS design tokens
- **Progressive Web App**: Web App Manifest (`manifest.json`), Service Worker (`sw.js`), Cache API
- **Payment Processing**: Paystack API (test-mode sandbox and HMAC SHA512 webhook handler)
- **Static Assets & Media**: WhiteNoise compressed static storage, Django media handler with optional Cloudinary support
- **Testing**: Django Automated Test Suite (`TestCase`, `Client`)

---

## 5. System Architecture

Hometrace is structured into 9 decoupled modular Django applications:

```
apps/
├── accounts/       # Custom User model, AgentProfile, BuyerProfile, Auth, RBAC
├── properties/     # Properties, Categories, Amenities, Images, Listing CRUD & Moderation
├── search/         # Multi-faceted search engine, query filtering, sorting, pagination
├── messaging/      # Conversations, Chat Messages, Client Enquiries, live polling API
├── favorites/      # Property bookmarks, AJAX toggle endpoint
├── payments/       # Paystack SDK integration, callback verification, webhooks, receipts
├── notifications/  # In-app notification center, alert dispatcher
├── dashboard/      # Agent, Buyer/Renter, and Administrator governance portals
└── core/           # Homepage, Static Pages, PWA Shell, Management Commands
```

---

## 6. Database Design & Models

| Model | Application | Purpose | Key Fields |
|---|---|---|---|
| `User` | `accounts` | Custom user model | `id (UUID)`, `email`, `role`, `full_name`, `phone_number`, `is_verified` |
| `AgentProfile` | `accounts` | Agency credentials | `agency_name`, `license_number`, `whatsapp_number`, `is_verified_agent` |
| `BuyerProfile` | `accounts` | Search preferences | `preferred_state`, `preferred_city`, `max_budget` |
| `PropertyCategory` | `properties` | Taxonomy | `name`, `slug`, `icon_name`, `description` |
| `Amenity` | `properties` | Nigerian utilities | `name`, `category (utility/security/comfort/luxury)` |
| `Property` | `properties` | Real estate listing | `title`, `slug`, `price`, `state`, `city`, `neighbourhood`, `approval_status`, `availability_status` |
| `PropertyImage` | `properties` | Photograph gallery | `image`, `caption`, `is_featured`, `display_order` |
| `PropertyReport` | `properties` | Scam moderation | `property`, `reporter`, `reason`, `description`, `status` |
| `Conversation` | `messaging` | Chat thread | `buyer`, `agent`, `property`, `updated_at` |
| `Message` | `messaging` | Chat message | `conversation`, `sender`, `body`, `is_read`, `created_at` |
| `Enquiry` | `messaging` | Formal inquiry | `buyer`, `agent`, `property`, `subject`, `message`, `status` |
| `Favorite` | `favorites` | Bookmarks | `user`, `property`, `created_at` (Unique together) |
| `Payment` | `payments` | Paystack audit | `reference`, `user`, `amount`, `purpose`, `status`, `paystack_reference` |
| `Notification` | `notifications` | System alerts | `user`, `title`, `message`, `notification_type`, `target_url`, `is_read` |

---

## 7. Installation & Quick Start Guide

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### Step 1: Clone Repository & Navigate
```bash
git clone https://github.com/your-username/hometrace.git
cd hometrace
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` settings work immediately out-of-the-box with SQLite and local Paystack sandbox simulation.

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```bash
python manage.py migrate
```

### Step 5: Seed Nigerian Demonstration Data
Populate the database with realistic demonstration accounts (Admin, Agents, Buyers), categories, amenities, properties across Lagos, Abuja, Rivers, Oyo, Nasarawa, conversations, and payment records:
```bash
python manage.py seed_data
```

### Step 6: Start the Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

## 8. Academic Defence Demo Credentials

The platform includes pre-seeded demonstration accounts with full test records:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **System Administrator** | `admin@hometrace.ng` | `AdminPass123!` | Complete administrative portal, moderation, user management, and ledger |
| **Property Agent** | `agent1@hometrace.ng` | `AgentPass123!` | Chief Babatunde Alabi (Apex Luxury Properties), listing management, inquiries, chat |
| **Property Agent** | `agent2@hometrace.ng` | `AgentPass123!` | Hajiya Amina Danjuma (Capital Prime Abuja), diplomatic listings |
| **Buyer / Renter** | `buyer1@hometrace.ng` | `BuyerPass123!` | Tariq Mohammed, saved properties, active chat threads, payment receipts |

*(Note: The login page at `/accounts/login/` features one-click autofill buttons for these accounts for instant defence demonstration.)*

---

## 9. Paystack Payment Gateway Testing

Hometrace integrates Paystack with strict server-side verification:
- **Sandbox Test Keys**: Set `PAYSTACK_PUBLIC_KEY` and `PAYSTACK_SECRET_KEY` in `.env`.
- **Supported Transactions**:
  1. *Agent Verification & Credential Audit*: ₦15,000 (awards Verified Agent badge).
  2. *Property Featured Spotlight*: ₦10,000 (promotes listing to homepage).
  3. *Physical Inspection Booking Deposit*: ₦5,000 (generates audit receipt).
- **Defence Simulation**: When running locally without active test cards, the checkout automatically presents an interactive sandbox simulator allowing examiners to test both successful authorizations and declines with full server verification and receipt generation.

---

## 10. Progressive Web Application (PWA) Verification

1. Open Google Chrome or Microsoft Edge and navigate to `http://127.0.0.1:8000/`.
2. Notice the "Install App" prompt in the navigation bar and bottom banner.
3. Click "Install" to install Hometrace as a native desktop or mobile standalone app.
4. **Offline Test**: Open Chrome DevTools (`F12`), navigate to the **Network** tab, toggle "Offline", and reload the page. The service worker seamlessly serves the offline shell at `/offline/`.

---

## 11. Automated Test Suite

Run the full automated test suite covering authentication, property CRUD, search filters, favorites, messaging, and payments:
```bash
python manage.py test
```

---

## 12. Security & Compliance

- **Role-Based Access Control (RBAC)**: All restricted routes are protected by `@agent_required`, `@buyer_required`, or `@admin_required` decorators.
- **CSRF Protection**: Enforced on all forms and state-changing actions.
- **SQL Injection Prevention**: Safe parameterization via Django ORM.
- **XSS Mitigation**: Strict HTML escaping across all Django templates.
- **Nigerian Data Privacy**: Password hashing via PBKDF2/SHA256, sensitive credentials isolated in `.env`.

---

## 13. Production Deployment Notes

For Vercel deployment:
1. Import the repository into Vercel. The included `vercel.json` and `api/index.py` configure the Django serverless entrypoint.
2. Add `SECRET_KEY`, `DATABASE_URL` (a persistent PostgreSQL database), `ALLOWED_HOSTS`, `PAYSTACK_PUBLIC_KEY`, and `PAYSTACK_SECRET_KEY` as Vercel environment variables.
3. Set `CLOUDINARY_URL` for persistent property and profile uploads. Vercel's filesystem is ephemeral, so local SQLite and local media storage are not suitable for production.
4. Static files are collected automatically during the Vercel build.

For other production platforms (e.g. on Ubuntu VPS, Render, Railway, or AWS):
1. Set `DEBUG=False` in `.env`.
2. Configure `ALLOWED_HOSTS=yourdomain.com`.
3. Provide PostgreSQL database connection string in `DATABASE_URL`.
4. Run `python manage.py collectstatic --noinput` (handled automatically via WhiteNoise).
5. Launch using Gunicorn / Uvicorn:
   ```bash
   gunicorn hometrace_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```
