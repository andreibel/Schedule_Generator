from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Schedule(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (User: {self.user.username})"


class Event(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time_slots = models.JSONField()
    def __str__(self):
        return f"{self.name} (Schedule: {self.schedule.name})"
    def clean(self):
        if not isinstance(self.time_slots, list):
            raise ValidationError("time_slots must be a list")
        for item in self.time_slots:
            if isinstance(item, list): #split time
                for time_slot in item:
                    if not isinstance(time_slot, str):
                        raise ValidationError("time_slot must be a string")
            elif not isinstance(item, str): #not split time
                raise ValidationError("time_slot must be a string")
    def is_split_schedule(self):
        return any(isinstance(item,list) for item in self.time_slots)

    def get_schedule_options(self):
        if self.is_split_schedule():
            return self.time_slots
        return [self.time_slots]
