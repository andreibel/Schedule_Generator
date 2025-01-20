from django.contrib import admin

# Register your models here.
from .models import Schedule, Event

admin.site.register(Schedule)
admin.site.register(Event)