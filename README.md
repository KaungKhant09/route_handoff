# Route Handoff

A Django-based mobile-first web application for two-step navigation (pickup → dropoff) using Google Maps deep links.

## Features

- Add and manage pickup and dropoff locations
- Select locations for navigation
- Two-step navigation flow with state tracking
- Google Maps deep link integration (mobile app + web fallback)
- Session-based state management
- Mobile-responsive design

## Requirements

- Python 3.8+
- Django 5.0+

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

5. Access the application at `http://127.0.0.1:8000/`

## Testing

Run the test suite:
```bash
python manage.py test
```

## Deployment

### Production Settings

Before deploying to production, update `route_handoff_project/settings.py`:

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS` with your domain
3. Set a strong `SECRET_KEY` (use environment variables)
4. Configure a production database (PostgreSQL recommended)
5. Set up static file serving (use `collectstatic` and a web server/CDN)

### Static Files

Collect static files for production:
```bash
python manage.py collectstatic
```

### Database Migration

Run migrations on production:
```bash
python manage.py migrate
```

### Security Considerations

- Use HTTPS in production
- Set secure session cookies
- Configure CSRF protection (enabled by default)
- Use environment variables for sensitive settings
- Regularly update dependencies

## Usage Flow

1. Add pickup and dropoff locations via the "Add" forms
2. Select a pickup location and dropoff location
3. Click "Navigate" to open Google Maps for the pickup location
4. After navigating to pickup, select dropoff (if not already selected)
5. Click "Navigate" again to open Google Maps for the dropoff location

## Architecture

- **Backend**: Django 5.x with function-based and class-based views
- **Database**: SQLite (development), PostgreSQL recommended for production
- **Frontend**: Django templates with mobile-first responsive CSS
- **State Management**: NavigationSession model linked to Django session keys
