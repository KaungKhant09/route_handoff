from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    path('', views.home, name='home'),
    path('locations/pickup/add/', views.PickUpCreateView.as_view(), name='pickup_add'),
    path('locations/dropoff/add/', views.DropOffCreateView.as_view(), name='dropoff_add'),
    path('locations/pickup/list/', views.PickUpListView.as_view(), name='pickup_list'),
    path('locations/dropoff/list/', views.DropOffListView.as_view(), name='dropoff_list'),
    path('select/', views.select_locations, name='select_locations'),
    path('navigate/', views.navigate_view, name='navigate_view'),
    path('navigate/action/', views.navigate_action, name='navigate_action'),
    path('start-over/', views.start_over, name='start_over'),
    path('state/', views.state_view, name='state_view'),
]
