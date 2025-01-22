from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import DetailView
import json
from .models import Schedule, Event
from django.views import generic
from django.core.exceptions import ValidationError

class IndexView(generic.ListView):
    template_name = 'Generator/index.html'
    context_object_name = 'last_schedules'

    def get_queryset(self):
        return Schedule.objects.order_by('-created_at')[:5]
class Detail_SchedualsView(generic.DetailView):
    template_name = 'Generator/details.html'
    context_object_name = 'schedule'
    pk_url_kwarg = 'request_id'
def detail(request,schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    return render(request,'Generator/details.html', {'schedule':schedule})
#
#
# def events(request, schedule_id):
#     schedule = get_object_or_404(Schedule, pk=schedule_id)
#
#     if request.method == 'POST':
#         # Initialize a dictionary to collect data for all events
#         event_data = {}
#
#         # Step 1: Parse the POST data to build event_data
#         for key, value in request.POST.items():
#             print(key, value)
#             if not key.startswith("event_"):
#                 continue
#             parts = key.split("_")
#             if len(parts) < 3:
#                 continue
#
#             event_index = parts[1]  # e.g., "0", "1", "2"
#             field_type = parts[2]   # e.g., "name" or "slot"
#
#             if event_index not in event_data:
#                 event_data[event_index] = {"name": "", "slots": []}
#
#             if field_type == "name":
#                 event_data[event_index]["name"] = value.strip()
#             elif field_type == "slot" and len(parts) == 5:
#                 # e.g., event_0_slot_1_day
#                 slot_index = parts[3]  # e.g., "1"
#                 slot_field = parts[4]  # e.g., "day", "start", "end"
#
#                 # Ensure the slot index exists
#                 while len(event_data[event_index]["slots"]) <= int(slot_index):
#                     event_data[event_index]["slots"].append({"day": "", "start": "", "end": ""})
#                 event_data[event_index]["slots"][int(slot_index)][slot_field] = value.strip()
#         print(event_data)
#         # Step 2: Iterate through all parsed events and save them
#         created_count = 0
#         for e_index, e_info in event_data.items():
#             name = e_info["name"]
#             slots = e_info["slots"]
#
#             # Build a list of formatted time slots
#             time_slot_list = []
#             for slot in slots:
#                 day = slot.get("day")
#                 start = slot.get("start")
#                 end = slot.get("end")
#                 if day and start and end:
#                     time_slot_list.append(f"{day} {start}-{end}")
#
#             # Skip if no name or no valid time slots
#             if not name or not time_slot_list:
#                 continue
#
#             # Create and save the event
#             try:
#
#                 new_event = Event(schedule=schedule, name=name, time_slots=time_slot_list)
#                 new_event.full_clean()  # Validate the event
#                 new_event.save()
#                 created_count += 1
#             except ValidationError as ve:
#                 # Log or display validation errors (optional)
#                 print(f"Validation error for event '{name}': {ve}")
#
#         return HttpResponse(f"Saved {created_count} new event(s) for schedule '{schedule.name}'.")
#
#     return HttpResponse("Please use POST to submit new events.")

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