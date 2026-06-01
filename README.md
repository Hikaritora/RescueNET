# RescueNet

A comprehensive **incident management and emergency response system** built with Django. RescueNet enables dispatchers and rescue teams to efficiently manage emergency incidents, coordinate resources, and track response operations in real-time.

![RescueNet](https://img.shields.io/badge/Django-6.0-green) ![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-blue)

<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/6e6effa5-4dc7-4078-8c9b-64a18c3c515b" />


## 🌟 Features

- **Incident Management**: Create, assign, track, and close emergency incidents
- **Resource Management**: Manage ambulances, police units, fire trucks, and technical equipment
- **Real-time Mapping**: Interactive map interface with Leaflet for incident and resource location tracking
- **Dynamic Resource Assignment**: Drag-and-drop resource assignment to incidents directly on the map
- **Role-Based Access Control**: Three user roles (Rescuer, Dispatcher, Admin) with fine-grained permissions
- **Analytics & Reporting**: Comprehensive charts showing incident types, statuses, and resource availability
- **Data Export**: Export incident reports to CSV
- **Demo Data Seeding**: Built-in command to populate sample data for testing

## 📋 User Roles & Permissions

| Role | Capabilities |
|------|---|
| **Rescuer** | View dashboard, incidents, resources, and reports (read-only) |
| **Dispatcher** | Create incidents, assign/unassign resources, close incidents |
| **Admin** | Full access + add/delete resources, manage resource availability |

See [ROLE_PERMISSIONS.md](ROLE_PERMISSIONS.md) for detailed permissions.

## 🏗️ Technology Stack

- **Backend**: Django 6.0.4
- **Database**: PostgreSQL 16+ (with psycopg2)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla + Chart.js, Leaflet)
- **Maps**: Leaflet 1.9.4, Carto, markers by [@pointhi](https://github.com/pointhi)
- **Charting**: Chart.js (for analytics dashboards)
- **Server**: ASGI (Uvicorn compatible with daphne)

## 📦 Prerequisites

Before installing RescueNet, ensure you have:

1. **Python 3.11 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **PostgreSQL 16, 17, or 18**
   - Download from: https://www.postgresql.org/download/
   - Remember the password you set for the `postgres` user

## 🚀 Installation

### Option 1: Automated Installation (Recommended)

The easiest way to get started is using the built-in setup script:

```bash
python setup.py
```

This will:
1. Create a virtual environment
2. Install all dependencies
3. Set up a PostgreSQL database
4. Run migrations
5. Create a demo superuser (username: `admin`, password: `admin`)
6. Optionally seed demo data
7. Optionally start the development server

**When prompted**, press Enter to accept default values, or customize as needed.

### Option 2: Manual Installation

If you prefer manual setup:

#### 1. Clone or navigate to the project directory
```bash
cd RescueNet
```

#### 2. Create and activate a virtual environment
**On Windows (PowerShell):**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Create a `.env` file in the project root
```ini
DATABASE_NAME=rescuenet
DATABASE_USER=postgres
DATABASE_PASSWORD=your_postgres_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DJANGO_SECRET_KEY=your_secret_key_here
RESCUENET_SUPERUSER_NAME=admin
RESCUENET_SUPERUSER_EMAIL=admin@example.com
RESCUENET_SUPERUSER_PASSWORD=admin
```

#### 5. Create the PostgreSQL database
```bash
psql -U postgres -c "CREATE DATABASE rescuenet;"
```

#### 6. Run migrations
```bash
python manage.py migrate
```

#### 7. Create a superuser
```bash
python manage.py createsuperuser
```

#### 8. (Optional) Seed demo data
```bash
python manage.py seed_database --admins 3 --dysp 50 --rescuers 50 --resources 60 --incidents 200
```

#### 9. Start the development server
```bash
python manage.py runserver
```

## 🎯 Quick Start

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Open your browser and navigate to:**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

3. **Log in with demo credentials:**
   - Username: `admin`
   - Password: `admin`

4. **Explore the dashboard:**
   - View active incidents
   - Create new incidents
   - Assign resources using the interactive map
   - View analytics and reports

## 📁 Project Structure

```
RescueNet/
├── core/                          # Django project settings
│   ├── settings.py               # Main Django configuration
│   ├── urls.py                   # URL routing
│   ├── wsgi.py                   # WSGI application
│   └── asgi.py                   # ASGI application
│
├── management/                    # Main Django app
│   ├── migrations/               # Database migrations
│   ├── static/
│   │   ├── css/                 # Static stylesheets
│   │   └── js/                  # Static JavaScript (map-picker)
│   ├── templates/
│   │   └── management/          # HTML templates
│   ├── models.py                # Database models (User, Incident, Resource)
│   ├── views.py                 # View logic
│   ├── forms.py                 # Django forms
│   ├── admin.py                 # Django admin configuration
│   └── management/
│       └── commands/
│           └── seed_database.py  # Demo data seeding command
│
├── setup.py                      # Automated installation script
├── manage.py                     # Django management CLI
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── ROLE_PERMISSIONS.md          # Detailed role documentation
├── LICENSE                      # License
└── .env                         # Environment configuration (created during setup)
```

## 🗂️ Key Models

### User
- Custom user model extending Django's AbstractUser
- Roles: `rescuer`, `dispatcher`, `admin`
- Role-based permission checking

### Incident
- Type (11 categories: Road Incident, Medical Emergency, Fire, etc.)
- Priority (Low, Medium, High, Critical)
- Status (Reported, In Progress, Closed)
- Location (latitude/longitude)
- Timestamps and reporter tracking

### Resource
- Type (Ambulance, Police, Fire Truck, Technical)
- Specialization (varies by type)
- Status (Available, Assigned, Unavailable)
- Location tracking and incident assignment

## 📊 Analytics

The **Reports & Archive** section provides visual analytics with four interactive charts:

1. **Incidents by Type** (Pie chart) - Distribution of incident types with distinct color palette
2. **Incidents Status** (Bar chart) - Count of reported, in-progress, and closed incidents
3. **Resources Types** (Pie chart) - Distribution of resources by type
4. **Resources Status** (Bar chart) - Count of available, assigned, and unavailable resources

## 🔧 Available Commands

### Run the development server
```bash
python manage.py runserver
```

### Create demo data
```bash
python manage.py seed_database --admins 3 --dysp 50 --rescuers 50 --resources 60 --incidents 200
```

### Apply migrations
```bash
python manage.py migrate
```

### Create a new superuser
```bash
python manage.py createsuperuser
```

### Access Django admin panel
Visit: http://127.0.0.1:8000/admin/

## 🔐 Security Notes

- All passwords must be configured via environment variables (`.env`)
- Permission checks are enforced server-side on all modifying endpoints
- The UI hides actions that users shouldn't perform, but protection is always server-side
- CSRF protection enabled on all forms
- Database credentials should never be committed to version control

## 📝 Environment Variables

The `.env` file (created during installation) contains:

```ini
DATABASE_NAME          # PostgreSQL database name
DATABASE_USER          # PostgreSQL user
DATABASE_PASSWORD      # PostgreSQL user password
DATABASE_HOST          # PostgreSQL host (default: localhost)
DATABASE_PORT          # PostgreSQL port (default: 5432)
DJANGO_SECRET_KEY      # Django secret key (auto-generated)
RESCUENET_SUPERUSER_NAME       # Default admin username
RESCUENET_SUPERUSER_EMAIL      # Default admin email
RESCUENET_SUPERUSER_PASSWORD   # Default admin password
```

## 🐛 Troubleshooting

### Database connection error
- Ensure PostgreSQL is running: `psql -U postgres -c "\l"`
- Check `.env` has correct database credentials
- Verify database exists: `psql -U postgres -c "\l rescuenet"`

### Virtual environment not activating
**Windows:** Use `.\venv\Scripts\Activate.ps1` (not `.venv\Scripts\...`)
**macOS/Linux:** Use `source .venv/bin/activate`

### Port 8000 already in use
```bash
python manage.py runserver 8001
```

### Missing dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Leaflet.js Documentation](https://leafletjs.com/reference.html)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)

## 👥 Created By

- [@Hikaritora](https://github.com/Hikaritora)
- [@Private-AS](https://github.com/Private-AS)
- [@ToTenPatryk](https://github.com/ToTenPatryk)

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/Hikaritora/RescueNET/blob/main/LICENSE) file for details.

This is a university course project. We are not affiliated with or related to any other projects or companies named "RescueNet".

---

**Made with ❤️ for emergency management systems**
