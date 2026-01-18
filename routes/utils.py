import re
from .models import NavigationSession


def get_or_create_navigation_session(request):
    """Get or create NavigationSession linked to current session key."""
    session_key = request.session.session_key
    if not session_key:
        # Ensure session is created
        request.session.create()
        session_key = request.session.session_key

    nav_session, created = NavigationSession.objects.get_or_create(
        session_key=session_key,
        defaults={'state': 'no_selection'}
    )
    return nav_session


def is_mobile_device(request):
    """Detect if request is from mobile device based on User-Agent."""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_patterns = [
        r'mobile', r'android', r'iphone', r'ipad', r'ipod',
        r'blackberry', r'windows phone', r'opera mini'
    ]
    return any(re.search(pattern, user_agent) for pattern in mobile_patterns)


def generate_maps_url(location, is_mobile=False):
    """
    Generate Google Maps deep link and web fallback URL for a location.
    Origin is always current GPS location (not specified, so Google Maps uses current location).
    
    Returns:
        dict: {'deep_link': str, 'web_fallback': str}
    """
    lat = str(location.latitude)
    lng = str(location.longitude)
    
    # Web fallback URL (works on all devices)
    # Not specifying origin makes Google Maps use current GPS location
    # travelmode=driving ensures driving directions
    web_fallback = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}&travelmode=driving"
    
    # Mobile deep links
    if is_mobile:
        # Android: google.navigation scheme always uses current location as origin
        # This will recalculate from current GPS every time
        android_deep_link = f"google.navigation:q={lat},{lng}"
        
        # iOS: comgooglemaps scheme uses current location if origin not specified
        # Not specifying saddr (source address) makes it use current location
        ios_deep_link = f"comgooglemaps://?daddr={lat},{lng}&directionsmode=driving"
        
        # Default to Android format (iOS will fallback if app not installed)
        # In practice, you might want to detect OS specifically
        deep_link = android_deep_link
    else:
        # Desktop: use web fallback
        deep_link = web_fallback
    
    return {
        'deep_link': deep_link,
        'web_fallback': web_fallback,
    }
