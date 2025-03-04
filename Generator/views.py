# Generator/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.shortcuts import redirect, get_object_or_404, render
from .models import Schedule, Event
from .forms import ScheduleForm
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils.generator import generate_possible_schedules, build_week_grid
from .templatetags import time_extras
import json

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
        event_data[event_index] = {"name": "", "mode": "single", "slots": {}} if event_index not in event_data else event_data[event_index]
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


@login_required
def generate_combinations_view(request, schedule_id):
    """
    Shows all possible schedules for a given schedule's events.
    """
    schedule = get_object_or_404(Schedule, pk=schedule_id, user=request.user)
    events = schedule.event_set.all()

    # Optional: read GET params, e.g. ?blocked_days=Thu&max_days=4
    blocked_days_param = request.GET.get('blocked_days', '')
    if blocked_days_param:
        blocked_days = set(d.strip() for d in blocked_days_param.split(','))
    else:
        blocked_days = None

    max_days_param = request.GET.get('max_days')
    if max_days_param and max_days_param.isdigit():
        max_days = int(max_days_param)
    else:
        max_days = None

    possible_schedules = generate_possible_schedules(
        events,
        blocked_days=blocked_days,
        max_days=max_days
    )


    context = {
        'schedule': schedule,
        'possible_schedules': possible_schedules,
        'blocked_days': blocked_days,
        'max_days': max_days,
    }

    st = ""
    for i in range(len(possible_schedules)):
        st+= f"Option {i+1}\n"
        for j in range(len(possible_schedules[i])):
            st += f"{possible_schedules[i][j][0]}: {possible_schedules[i][j][1]} {time_extras.minutes_to_hhmm(possible_schedules[i][j][2])} - {time_extras.minutes_to_hhmm(possible_schedules[i][j][3])}\n"

    lines = st.strip().splitlines()
    parsed_data = []

    current_option_number = None
    current_courses = []

    for line in lines:
        line = line.strip()
        if not line:
            # Skip blank lines
            continue

        # Check if this line begins a new Option
        if line.startswith("Option"):
            # If we were already collecting courses for a previous option,
            # save them before starting a new one.
            if current_option_number is not None:
                parsed_data.append({
                    "option_number": current_option_number,
                    "courses": current_courses
                })

            # Extract the option number after the word "Option"
            # Example: "Option 11" => we take "11"
            parts = line.split()
            current_option_number = parts[1]  # "11" in that example
            current_courses = []  # Reset course list for new option
        else:
            # It's a course line of the format:
            # "course_name: Day start - end"
            # Example: "תכנות מונחה עצמים - הרצאה: Thu 10:30 - 13:50"
            if ':' not in line:
                continue  # skip malformed lines

            course_part, times_part = line.split(':', 1)
            course_part = course_part.strip()  # e.g. "תכנות מונחה עצמים - הרצאה"
            times_part = times_part.strip()  # e.g. "Thu 10:30 - 13:50"

            # times_part typically: "Thu 10:30 - 13:50"
            # We'll split by spaces
            tokens = times_part.split()
            # tokens[0] = "Thu"
            # tokens[1] = "10:30"
            # tokens[2] = "-"
            # tokens[3] = "13:50"
            if len(tokens) >= 4:
                day = tokens[0]
                start = tokens[1]
                end = tokens[3]

                current_courses.append({"name": course_part, "day": day, "start": start, "end": end})

    # Don't forget to add the last option's data at the end of the file
    if current_option_number is not None and current_courses:
        parsed_data.append({
            "option_number": current_option_number,
            "courses": current_courses
        })

    new_list = []
    for i in parsed_data:
        new_list.append(i.get("courses"))
    context = json.dumps(new_list, ensure_ascii=False, indent=2)

    l = {"data": context}
    return render(request, 'Generator/possible_schedules.html', l)


@login_required
def weekly_calendar_view(request, schedule_id):
    """
    Shows one schedule (the first valid schedule) in a weekly calendar format.
    """
    schedule = get_object_or_404(Schedule, pk=schedule_id, user=request.user)
    events = schedule.event_set.all()

    # Generate all valid combos
    all_schedules = generate_possible_schedules(events)
    if not all_schedules:
        # No valid combos
        return render(request, 'Generator/no_schedules.html', {"schedule": schedule})

    # Just pick the first valid schedule
    first_sched = all_schedules[0]  # list of (ev_name, day, start, end)
    grid_data = build_week_grid(first_sched, start_hour=8, end_hour=18, interval=30)

    context = {
        "schedule": schedule,
        "this_schedule": first_sched,
        "grid_data": grid_data,
        "num_schedules": len(all_schedules),
    }
    return render(request, 'Generator/weekly_calendar.html', context)