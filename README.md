# Healthcare Backend API

A comprehensive Django REST API for healthcare management, supporting patient records, doctor management, and patient-doctor relationships with JWT authentication.

## Features

- **User Authentication**: JWT-based registration, login, and profile management
- **Patient Management**: CRUD operations for patient records with user isolation
- **Doctor Management**: Complete doctor profile management
- **Patient-Doctor Relationships**: Assign/unassign doctors to patients
- **Search & Filtering**: Advanced search capabilities across all entities
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Comprehensive Testing**: Full test coverage for all endpoints
- **Error Handling**: Consistent error responses and logging

## Tech Stack

- **Backend**: Django 5.1.4, Django REST Framework 3.15.2
- **Authentication**: JWT with djangorestframework-simplejwt
- **Database**: PostgreSQL (configurable)
- **Documentation**: drf-yasg for Swagger/OpenAPI
- **Testing**: Django's built-in test framework
- **Other**: django-cors-headers, django-filter

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd healthcare-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file based on `.env.bhuvan`:

```bash
cp .env.bhuvan .env
```

Update the `.env` file with your database credentials and other settings.

### 3. Database Setup

#### Option A: Quick Development Setup (SQLite)
```bash
# Easy development server with SQLite
python start_dev.py
```

#### Option B: Production Setup (PostgreSQL)
```bash
# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run with production settings
python manage.py runserver
```

#### Option C: Manual Development Setup
```bash
# Use SQLite for development
python manage.py migrate --settings=config.settings_dev
python manage.py createsuperuser --settings=config.settings_dev
python manage.py runserver --settings=config.settings_dev
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/auth/register/` | User registration |
| POST | `/api/v1/users/auth/login/` | User login |
| POST | `/api/v1/users/auth/token/refresh/` | Refresh JWT token |
| GET | `/api/v1/users/profile/` | Get user profile |
| PUT/PATCH | `/api/v1/users/profile/` | Update user profile |
| POST | `/api/v1/users/profile/change-password/` | Change password |

### Patient Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health/patients/` | List user's patients |
| POST | `/api/v1/health/patients/` | Create new patient |
| GET | `/api/v1/health/patients/{id}/` | Get patient details |
| PUT/PATCH | `/api/v1/health/patients/{id}/` | Update patient |
| DELETE | `/api/v1/health/patients/{id}/` | Delete patient |
| POST | `/api/v1/health/patients/{id}/assign_doctor/` | Assign doctor to patient |
| DELETE | `/api/v1/health/patients/{id}/unassign_doctor/` | Unassign doctor from patient |

### Doctor Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health/doctors/` | List all doctors |
| POST | `/api/v1/health/doctors/` | Create new doctor |
| GET | `/api/v1/health/doctors/{id}/` | Get doctor details |
| PUT/PATCH | `/api/v1/health/doctors/{id}/` | Update doctor |
| DELETE | `/api/v1/health/doctors/{id}/` | Delete doctor |
| GET | `/api/v1/health/doctors/{id}/patients/` | Get doctor's patients |

### Patient-Doctor Relationships

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health/patient-doctors/` | List relationships |
| POST | `/api/v1/health/patient-doctors/` | Create relationship |
| DELETE | `/api/v1/health/patient-doctors/{id}/` | Delete relationship |

## API Documentation

- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/redoc/`
- **Admin Interface**: `http://127.0.0.1:8000/admin/`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Registration Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/auth/register/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### Login Example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/auth/login/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

## Data Models

### Patient
- `name`: CharField (required)
- `age`: PositiveIntegerField (optional)
- `gender`: CharField (optional)
- `notes`: TextField (optional)
- `created_by`: ForeignKey to User
- `created_at`: DateTimeField (auto)
- `updated_at`: DateTimeField (auto)

### Doctor
- `name`: CharField (required)
- `specialization`: CharField (optional)
- `email`: EmailField (unique, required)
- `phone`: CharField (optional)
- `created_at`: DateTimeField (auto)
- `updated_at`: DateTimeField (auto)

### PatientDoctor (Relationship)
- `patient`: ForeignKey to Patient
- `doctor`: ForeignKey to Doctor
- `created_at`: DateTimeField (auto)

## Search and Filtering

### Patients
- **Search**: `?search=john` (searches name and notes)
- **Filter**: `?gender=Male&created_by=1`
- **Ordering**: `?ordering=name` or `?ordering=-created_at`

### Doctors
- **Search**: `?search=cardiology` (searches name, email, specialization)
- **Filter**: `?specialization=Cardiology`
- **Ordering**: `?ordering=name`

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test health

# Run with coverage (install coverage first)
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Validation error",
    "details": {
      "field_name": ["Error message"]
    }
  }
}
```

## Security Features

- JWT token-based authentication
- User isolation (users can only access their own patients)
- Password validation
- CORS configuration
- Input validation and sanitization
- Proper error handling without information leakage

## Production Deployment

### Environment Variables

Set the following environment variables in production:

```env
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
POSTGRES_DB=healthcare_prod
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=your_db_host
POSTGRES_PORT=5432
CORS_ALLOW_ALL_ORIGINS=False
```

### Database Setup

Ensure PostgreSQL is installed and create the database:

```sql
CREATE DATABASE healthcare_prod;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE healthcare_prod TO your_db_user;
```

### Static Files and Media

Configure static files collection:

```bash
python manage.py collectstatic
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Support

For support, please contact [your-email@example.com] or create an issue in the repository.