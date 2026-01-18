from django.db import models


class PickUpLocation(models.Model):
    """Model for storing pickup locations."""
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pickup Location'
        verbose_name_plural = 'Pickup Locations'

    def __str__(self):
        return self.name


class DropOffLocation(models.Model):
    """Model for storing dropoff locations."""
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Dropoff Location'
        verbose_name_plural = 'Dropoff Locations'

    def __str__(self):
        return self.name


class NavigationSession(models.Model):
    """Model for tracking navigation state and selections per session."""
    STATE_CHOICES = [
        ('no_selection', 'No Selection'),
        ('pickup_selected', 'Pickup Selected'),
        ('navigated_to_pickup', 'Navigated to Pickup'),
        ('dropoff_selected', 'Dropoff Selected'),
        ('navigated_to_dropoff', 'Navigated to Dropoff'),
        ('completed', 'Completed'),
    ]

    session_key = models.CharField(max_length=40, db_index=True)
    pickup = models.ForeignKey(
        PickUpLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    dropoff = models.ForeignKey(
        DropOffLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='no_selection'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Navigation Session'
        verbose_name_plural = 'Navigation Sessions'

    def __str__(self):
        return f"Session {self.session_key[:8]}... - {self.get_state_display()}"
