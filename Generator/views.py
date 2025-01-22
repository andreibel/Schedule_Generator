from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import DetailView
import json
from .models import Schedule, Event
from django.views import generic
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'Generator/index.html'
    context_object_name = 'last_schedules'
    login_url = '/accounts/login/'

    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)

class Detail_SchedualsView(LoginRequiredMixin, generic.DetailView):
    template_name = 'Generator/details.html'
    context_object_name = 'schedule'
    pk_url_kwarg = 'request_id'
@login_required(login_url='/accounts/login/')
def detail(request,schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    return render(request,'Generator/details.html', {'schedule':schedule})
@login_required(login_url='/accounts/login/')
def events(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
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

    return HttpResponse(f"Saved {created_count} new event(s) for schedule '{schedule.name}'.")