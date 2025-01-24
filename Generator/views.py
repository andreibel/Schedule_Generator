# Generator/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from .models import Schedule, Event
from .forms import ScheduleForm
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required

class IndexView(LoginRequiredMixin, ListView):
    template_name = 'Generator/index.html'
    context_object_name = 'user_schedules'
    login_url = '/accounts/login/'

    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)

class CreateScheduleView(LoginRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'Generator/index.html'  # Reuse index.html to display form
    login_url = '/accounts/login/'

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associate the schedule with the current user
        schedule = form.save()
        messages.success(self.request, f"Schedule '{schedule.name}' created successfully!")
        return redirect('generator:detail', schedule_id=schedule.id)

@login_required(login_url='/accounts/login/')
def detail(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id, user=request.user)
    return render(request, 'Generator/details.html', {'schedule': schedule})

@login_required(login_url='/accounts/login/')
def events(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id, user=request.user)
    if request.method != 'POST':
        return HttpResponse("Please use POST to submit events.")

    # Build a dictionary to hold data for each event.
    event_data = {}
    for key, value in request.POST.items():
        if not key.startswith("event_"):
            continue
        parts = key.split("_")
        if len(parts) < 3:
            continue
        event_index = parts[1]
        field = parts[2]
        if event_index not in event_data:
            # Initialize with default values.
            event_data[event_index] = {"name": "", "mode": "single", "slots": {}}
        if field == "name":
            event_data[event_index]["name"] = value.strip()
        elif field == "mode":
            event_data[event_index]["mode"] = value.strip()
        elif field == "slot":
            # For single mode, expect: event_X_slot_Y_day/start/end  (length = 5)
            # For split mode, expect: event_X_slot_Y_first_day/start/end or
            # event_X_slot_Y_second_day/start/end (length = 6)
            if len(parts) == 5:
                slot_index = parts[3]
                slot_field = parts[4]
                if slot_index not in event_data[event_index]["slots"]:
                    event_data[event_index]["slots"][slot_index] = {}
                event_data[event_index]["slots"][slot_index][slot_field] = value.strip()
            elif len(parts) == 6:
                slot_index = parts[3]
                part_indicator = parts[4]  # "first" or "second"
                slot_field = parts[5]
                if slot_index not in event_data[event_index]["slots"]:
                    event_data[event_index]["slots"][slot_index] = {}
                if part_indicator not in event_data[event_index]["slots"][slot_index]:
                    event_data[event_index]["slots"][slot_index][part_indicator] = {}
                event_data[event_index]["slots"][slot_index][part_indicator][slot_field] = value.strip()

    created_count = 0
    for e_idx, e_info in event_data.items():
        name = e_info.get("name", "")
        mode = e_info.get("mode", "single")
        slots = e_info.get("slots", {})
        # Skip events without a name or without any slot data.
        if not name or not slots:
            continue

        if mode == "single":
            time_slots = []
            for slot in slots.values():
                day = slot.get("day")
                start = slot.get("start")
                end = slot.get("end")
                if day and start and end:
                    time_slots.append(f"{day} {start}-{end}")
            if not time_slots:
                continue
        elif mode == "split":
            time_slots = []
            for slot in slots.values():
                # In split mode, both "first" and "second" parts are required.
                first = slot.get("first", {})
                second = slot.get("second", {})
                if (first.get("day") and first.get("start") and first.get("end") and
                        second.get("day") and second.get("start") and second.get("end")):
                    group = [f"{first.get('day')} {first.get('start')}-{first.get('end')}",
                             f"{second.get('day')} {second.get('start')}-{second.get('end')}"]
                    time_slots.append(group)
            if not time_slots:
                continue
        else:
            continue  # Unknown mode

        # Create and save the event.
        try:
            new_event = Event(schedule=schedule, name=name, time_slots=time_slots)
            new_event.full_clean()
            new_event.save()
            created_count += 1
        except ValidationError as ve:
            return HttpResponse(f"Validation error for event '{name}': {ve.message_dict}")

    messages.success(request, f"Saved {created_count} new event(s) for schedule '{schedule.name}'.")
    return redirect('generator:detail', schedule_id=schedule.id)