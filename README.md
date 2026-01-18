# Route Handoff

A Django-based mobile-first web application for two-step navigation (pickup → dropoff) using Google Maps deep links. The app guides users through sequential navigation: first to a pickup location, then to a dropoff location, always using the device's current GPS location as the origin.

## Features

- **Location Management**: Add and manage pickup and dropoff locations with name and coordinates
- **Two-Step Navigation**: Sequential navigation flow with backend state tracking
- **Google Maps Integration**: 
  - Mobile: Opens Google Maps app via deep links (`google.navigation:` for Android, `comgooglemaps://` for iOS)
  - Desktop/Web: Opens Google Maps web interface
  - Always uses current GPS location as origin
- **State Management**: Database-backed navigation session tracking with state transitions
- **Mobile-First Design**: Responsive UI optimized for mobile devices
- **Session-Based**: Works without authentication - uses Django session keys

## Requirements

- Python 3.11+ (see `runtime.txt`)
- Django 5.0+
- For production: Gunicorn, WhiteNoise (already in requirements.txt)

## Project Structure

```
route_handoff_project/
├── manage.py
├── Procfile                    # Railway deployment config
├── runtime.txt                 # Python version
├── requirements.txt            # Python dependencies
├── RAILWAY_DEPLOYMENT.md       # Detailed Railway deployment guide
├── route_handoff_project/      # Django project settings
│   ├── settings.py            # Config (uses environment variables)
│   ├── urls.py                # Root URLconf
│   └── wsgi.py                # WSGI config
└── routes/                     # Main application
    ├── models.py              # PickUpLocation, DropOffLocation, NavigationSession
    ├── views.py               # CBV for CRUD, FBV for navigation logic
    ├── urls.py                # App URL patterns
    ├── forms.py               # LocationForm for validation
    ├── utils.py               # Deep link generation, device detection
    ├── templates/routes/      # Django templates
    ├── static/routes/         # CSS and JavaScript
    └── tests.py               # Unit and integration tests
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)

For Django admin access:

```bash
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`

## Usage Flow

1. **Add Locations**: 
   - Navigate to "Pickups" or "Dropoffs" menu
   - Click "Add New" to create locations with name, latitude, and longitude

2. **Select Locations**: 
   - Go to "Select Locations" page
   - Choose one pickup location and one dropoff location
   - Click "Confirm Selections"

3. **Navigate to Pickup**: 
   - On the Navigation page, click "Navigate to Pickup"
   - Google Maps opens (app on mobile, web on desktop) with directions from your current location to the pickup point
   - The page stays open so you can navigate again

4. **Navigate to Dropoff**: 
   - After navigating to pickup, the button automatically changes to "Navigate to Dropoff"
   - Click the button to open Google Maps with directions from your current location to the dropoff point

**Key Features:**
- Navigation always uses **current GPS location** as origin (not specified in URL, so Google Maps uses device location)
- Button text updates automatically based on navigation state
- Maps open in a separate window/tab, keeping the app page accessible

## URL Routes

- `/` - Home (redirects based on state)
- `/locations/pickup/add/` - Add pickup location
- `/locations/dropoff/add/` - Add dropoff location
- `/locations/pickup/list/` - List pickup locations
- `/locations/dropoff/list/` - List dropoff locations
- `/select/` - Select pickup and dropoff locations
- `/navigate/` - Navigation page with button
- `/navigate/action/` - Process navigation (POST only)
- `/start-over/` - Reset navigation session
- `/state/` - View current navigation state (debug/info)

## Testing

Run the test suite:

```bash
python manage.py test
```

The test suite includes:
- Model tests (PickUpLocation, DropOffLocation, NavigationSession)
- View tests (CRUD operations, navigation flow)
- State transition tests
- Utility function tests (deep link generation, device detection)

## Deployment

### Railway (Recommended)

The project is configured for easy deployment on Railway. See `RAILWAY_DEPLOYMENT.md` for detailed step-by-step instructions.

**Quick Railway Setup:**
1. Push code to GitHub
2. Create Railway project and connect repository
3. Add environment variables: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`
4. Add PostgreSQL database (Railway auto-creates `DATABASE_URL`)
5. Railway auto-deploys on git push

### Manual Production Setup

1. **Environment Variables** (required):
   ```bash
   SECRET_KEY=your-secure-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Database**: Configure PostgreSQL or your preferred database
   - Update `DATABASE_URL` or modify `DATABASES` in `settings.py`

3. **Static Files**: 
   ```bash
   python manage.py collectstatic --noinput
   ```
   WhiteNoise middleware is configured to serve static files.

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start Server**: Use Gunicorn (configured in `Procfile`):
   ```bash
   gunicorn route_handoff_project.wsgi --log-file -
   ```

## Architecture

### Backend
- **Framework**: Django 5.x
- **Views**: Mix of Class-Based Views (CRUD) and Function-Based Views (navigation logic)
- **Database**: SQLite (development), PostgreSQL (production)
- **State Management**: `NavigationSession` model with state transitions:
  - `no_selection` → `pickup_selected` → `navigated_to_pickup` → `dropoff_selected` → `navigated_to_dropoff`

### Frontend
- **Templates**: Django template engine
- **CSS**: Mobile-first responsive design (`static/routes/css/style.css`)
- **JavaScript**: Minimal vanilla JS for UX enhancements (`static/routes/js/main.js`)
- **Static Files**: Served via WhiteNoise middleware in production

### Google Maps Integration
- **Mobile Deep Links**:
  - Android: `google.navigation:q=<lat>,<lng>`
  - iOS: `comgooglemaps://?daddr=<lat>,<lng>&directionsmode=driving`
- **Web Fallback**: `https://www.google.com/maps/dir/?api=1&destination=<lat>,<lng>&travelmode=driving`
- **Origin**: Always current GPS location (not specified, so Google Maps uses device location)

### State Transitions

```
no_selection
    ↓ (select pickup)
pickup_selected
    ↓ (click Navigate)
navigated_to_pickup
    ↓ (select dropoff)
dropoff_selected
    ↓ (click Navigate)
navigated_to_dropoff
    ↓ (optional)
completed
```

## Configuration

### Settings

The `settings.py` uses environment variables for production-ready configuration:

- `SECRET_KEY`: Django secret key (required in production)
- `DEBUG`: Debug mode (set to `False` in production)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Dependencies

- `Django>=5.0,<6.0` - Web framework
- `gunicorn>=21.2.0` - WSGI HTTP server for production
- `whitenoise>=6.6.0` - Static file serving in production

## Security Considerations

- ✅ CSRF protection enabled (Django default)
- ✅ Environment variables for sensitive settings
- ✅ `DEBUG=False` in production
- ✅ `ALLOWED_HOSTS` configured (not wildcard in production)
- ✅ WhiteNoise for secure static file serving
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection (Django template auto-escaping)

## Troubleshooting

### Common Issues

1. **Static files not loading**: Ensure WhiteNoise is in `MIDDLEWARE` and run `collectstatic`
2. **Navigation button not updating**: Check navigation session state in admin or `/state/` page
3. **Maps not opening on mobile**: Verify deep link URL format and Google Maps app installation
4. **Session state lost**: Navigation sessions are tied to Django session keys - clearing cookies resets state

### Debug Mode

To enable debug mode locally, set:
```bash
export DEBUG=True
```

Or in `settings.py`, temporarily change:
```python
DEBUG = True
```

## Development

### Running Tests

```bash
python manage.py test routes
```

### Creating Migrations

After model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface

Access Django admin at `/admin/` after creating a superuser:
- Manage locations
- View navigation sessions
- Debug state transitions

## License

This project is open source and available for use.

## Support

For deployment help, see `RAILWAY_DEPLOYMENT.md` for detailed Railway deployment instructions.
