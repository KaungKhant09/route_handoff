from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import PickUpLocation, DropOffLocation, NavigationSession
from .forms import PickUpLocationForm, DropOffLocationForm
from .utils import get_or_create_navigation_session


class PickUpCreateView(CreateView):
    """View for creating pickup locations."""
    model = PickUpLocation
    form_class = PickUpLocationForm
    template_name = 'routes/location_form.html'
    success_url = reverse_lazy('routes:pickup_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_type'] = 'pickup'
        return context


class DropOffCreateView(CreateView):
    """View for creating dropoff locations."""
    model = DropOffLocation
    form_class = DropOffLocationForm
    template_name = 'routes/location_form.html'
    success_url = reverse_lazy('routes:dropoff_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_type'] = 'dropoff'
        return context


class PickUpListView(ListView):
    """View for listing pickup locations."""
    model = PickUpLocation
    template_name = 'routes/location_list.html'
    context_object_name = 'locations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_type'] = 'pickup'
        nav_session = get_or_create_navigation_session(self.request)
        context['current_selection'] = nav_session.pickup_id if nav_session.pickup else None
        return context


class DropOffListView(ListView):
    """View for listing dropoff locations."""
    model = DropOffLocation
    template_name = 'routes/location_list.html'
    context_object_name = 'locations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_type'] = 'dropoff'
        nav_session = get_or_create_navigation_session(self.request)
        context['current_selection'] = nav_session.dropoff_id if nav_session.dropoff else None
        return context


def home(request):
    """Home view that redirects based on current state."""
    nav_session = get_or_create_navigation_session(request)
    if nav_session.state == 'no_selection' or not nav_session.pickup:
        return redirect('routes:select_locations')
    return redirect('routes:navigate_view')


def select_locations(request):
    """View for selecting pickup and dropoff locations."""
    nav_session = get_or_create_navigation_session(request)

    if request.method == 'POST':
        pickup_id = request.POST.get('pickup_id')
        dropoff_id = request.POST.get('dropoff_id')

        # Update pickup selection
        if pickup_id:
            pickup = get_object_or_404(PickUpLocation, id=pickup_id)
            nav_session.pickup = pickup
            # If pickup is changed after dropoff was selected, reset dropoff if state allows
            if nav_session.state in ['dropoff_selected', 'navigated_to_dropoff']:
                nav_session.dropoff = None
                nav_session.state = 'pickup_selected'
            elif nav_session.state == 'no_selection':
                nav_session.state = 'pickup_selected'
            nav_session.save()

        # Update dropoff selection
        if dropoff_id:
            dropoff = get_object_or_404(DropOffLocation, id=dropoff_id)
            nav_session.dropoff = dropoff
            if nav_session.state == 'navigated_to_pickup':
                nav_session.state = 'dropoff_selected'
            nav_session.save()

        messages.success(request, 'Locations selected successfully.')
        return redirect('routes:navigate_view')

    # GET: Display selection form
    pickups = PickUpLocation.objects.all()
    dropoffs = DropOffLocation.objects.all()
    
    context = {
        'pickups': pickups,
        'dropoffs': dropoffs,
        'nav_session': nav_session,
    }
    return render(request, 'routes/select_locations.html', context)


def navigate_view(request):
    """View for displaying navigate page with button."""
    nav_session = get_or_create_navigation_session(request)

    # Validate state - ensure pickup is selected
    if not nav_session.pickup:
        messages.error(request, 'Please select a pickup location first.')
        return redirect('routes:select_locations')

    # State consistency check - if state says dropoff is selected but no dropoff, reset
    if nav_session.state in ['dropoff_selected', 'navigated_to_dropoff'] and not nav_session.dropoff:
        nav_session.state = 'navigated_to_pickup'
        nav_session.save()
        messages.warning(request, 'Dropoff location was cleared. Please select a dropoff location.')

    from .utils import generate_maps_url, is_mobile_device
    is_mobile = is_mobile_device(request)

    # Determine target location based on state
    # First navigate: Origin = current GPS, Destination = pickup
    # Second navigate: Origin = current GPS, Destination = dropoff
    if nav_session.state == 'pickup_selected':
        # First navigation: go to pickup from current location
        target_location = nav_session.pickup
        button_label = 'Navigate to Pickup'
    elif nav_session.state == 'navigated_to_pickup' and nav_session.dropoff:
        # After reaching pickup, next navigation goes to dropoff from current location
        target_location = nav_session.dropoff
        button_label = 'Navigate to Dropoff'
    elif nav_session.state in ['dropoff_selected', 'navigated_to_dropoff']:
        # Dropoff navigation
        if not nav_session.dropoff:
            messages.error(request, 'Please select a dropoff location first.')
            return redirect('routes:select_locations')
        target_location = nav_session.dropoff
        button_label = 'Navigate to Dropoff'
    else:
        # Default: navigate to pickup (first navigation)
        target_location = nav_session.pickup
        button_label = 'Navigate to Pickup'

    urls = generate_maps_url(target_location, is_mobile)

    # Check if there's a navigate URL in session (from navigate_action)
    # This means we just updated state and should open maps in new window
    navigate_url = request.session.pop('navigate_url', None)
    navigate_url_web_fallback = request.session.pop('navigate_url_web_fallback', None)

    context = {
        'navigation_session': nav_session,
        'deep_link_url': urls['deep_link'],
        'web_fallback_url': urls['web_fallback'],
        'button_label': button_label,
        'target_location': target_location,
        'auto_navigate_url': navigate_url,  # URL to auto-open in new window
        'auto_navigate_url_web_fallback': navigate_url_web_fallback,
    }
    return render(request, 'routes/navigate.html', context)


def navigate_action(request):
    """Process navigate button click - generate deep link and update state."""
    if request.method != 'POST':
        return redirect('routes:navigate_view')

    nav_session = get_or_create_navigation_session(request)

    # Validate state and selections
    if not nav_session.pickup:
        messages.error(request, 'Please select a pickup location first.')
        return redirect('routes:select_locations')

    # Determine next state and target location
    # Origin is always current GPS location (handled by generate_maps_url)
    if nav_session.state == 'pickup_selected':
        # First navigation: go to pickup from current location
        nav_session.state = 'navigated_to_pickup'
        nav_session.save()
        target_location = nav_session.pickup
    elif nav_session.state == 'navigated_to_pickup' and nav_session.dropoff:
        # After reaching pickup, next navigation goes to dropoff from current location
        nav_session.state = 'navigated_to_dropoff'
        nav_session.save()
        target_location = nav_session.dropoff
    elif nav_session.state == 'dropoff_selected':
        # Navigate to dropoff from current location
        nav_session.state = 'navigated_to_dropoff'
        nav_session.save()
        target_location = nav_session.dropoff
    elif nav_session.state == 'navigated_to_dropoff':
        # Re-navigating to dropoff from current location
        target_location = nav_session.dropoff
    else:
        # Default: navigate to pickup from current location
        nav_session.state = 'navigated_to_pickup'
        nav_session.save()
        target_location = nav_session.pickup

    # Generate maps URLs and store in session for JavaScript to open in new window
    from .utils import generate_maps_url, is_mobile_device
    is_mobile = is_mobile_device(request)
    urls = generate_maps_url(target_location, is_mobile)

    # Store the URL in session so JavaScript can open it in a new window
    # This keeps the user on the app page so they can navigate again
    request.session['navigate_url'] = urls['deep_link'] if is_mobile else urls['web_fallback']
    request.session['navigate_url_web_fallback'] = urls['web_fallback']
    
    # Redirect back to navigate view - JavaScript will open maps in new window
    return redirect('routes:navigate_view')


def state_view(request):
    """Display current navigation session state (for debugging/info)."""
    nav_session = get_or_create_navigation_session(request)
    context = {
        'nav_session': nav_session,
    }
    return render(request, 'routes/navigation_state.html', context)


def start_over(request):
    """Reset navigation session to initial state."""
    nav_session = get_or_create_navigation_session(request)
    nav_session.pickup = None
    nav_session.dropoff = None
    nav_session.state = 'no_selection'
    nav_session.save()
    messages.info(request, 'Navigation session reset. Please select locations again.')
    return redirect('routes:select_locations')
