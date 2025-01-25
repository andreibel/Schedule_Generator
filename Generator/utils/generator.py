# Generator/utils/generator_utils.py

from itertools import product


#
# --- 1) Parsing day/time ---
#
def parse_day_time(time_str):
    """
    "Mon 08:30-10:20" -> ("Mon", start_minutes, end_minutes).
    """
    parts = time_str.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid time slot format: {time_str}")
    day, hours_range = parts
    start_str, end_str = hours_range.split('-')
    start_minutes = _to_minutes(start_str)
    end_minutes = _to_minutes(end_str)
    return (day, start_minutes, end_minutes)


def _to_minutes(hh_mm):
    hh, mm = hh_mm.split(':')
    return int(hh) * 60 + int(mm)


#
# --- 2) Collecting all options for an Event ---
#
def get_event_options(event):
    """
    Returns a list of possible "options" for this event. 
    Each "option" is a list of tuples: (event.name, day, start, end).
    """
    if event.is_split_schedule():
        # event.time_slots is a list of lists
        # e.g. [
        #   ["Mon 08:30-10:20", "Wed 10:30-12:20"], 
        #   ["Mon 09:30-11:20", "Fri 08:30-10:20"]
        # ]
        results = []
        for sublist in event.time_slots:
            parsed_times = []
            for slot_str in sublist:
                day, start, end = parse_day_time(slot_str)
                parsed_times.append((event.name, day, start, end))
            results.append(parsed_times)
        return results
    else:
        # event.time_slots is a single list of strings
        # e.g. ["Tue 08:30-10:20", "Wed 10:30-12:20"]
        # We'll treat each string as a separate option:
        results = []
        for slot_str in event.time_slots:
            day, start, end = parse_day_time(slot_str)
            results.append([(event.name, day, start, end)])
        return results


#
# --- 3) Checking conflicts and conditions ---
#
def has_conflicts(slot_list):
    """
    slot_list is [(ev_name, day, start, end), ...].
    Conflicts occur if times overlap on the same day.
    """
    # Focus on (day, start, end)
    sorted_slots = sorted(slot_list, key=lambda x: (x[1], x[2]))
    # x[1] = day, x[2] = start
    for i in range(1, len(sorted_slots)):
        prev = sorted_slots[i - 1]
        curr = sorted_slots[i]
        prev_day, prev_start, prev_end = prev[1], prev[2], prev[3]
        curr_day, curr_start, curr_end = curr[1], curr[2], curr[3]
        if prev_day == curr_day and curr_start < prev_end:
            return True
    return False


def contains_blocked_days(slot_list, blocked_days):
    if not blocked_days:
        return False
    for (ev_name, day, start, end) in slot_list:
        if day in blocked_days:
            return True
    return False


def meets_max_days_condition(slot_list, max_days):
    if not max_days:
        return True
    unique_days = set(item[1] for item in slot_list)  # item[1] = day
    return len(unique_days) <= max_days


#
# --- 4) Generate all possible schedules ---
#
def generate_possible_schedules(events, blocked_days=None, max_days=None):
    """
    Return a list of valid schedules, each schedule is:
      [ (event_name, day, start, end), ... ]
    """
    if blocked_days is None:
        blocked_days = set()

    # Build a list of "option" lists
    event_options_list = [get_event_options(ev) for ev in events]

    # Cartesian product
    all_combos = product(*event_options_list)

    valid_schedules = []
    for combo in all_combos:
        # combo is a tuple of sublists
        # Flatten them into one list
        schedule_slots = []
        for sublist in combo:
            schedule_slots.extend(sublist)

        # Check conditions
        if has_conflicts(schedule_slots):
            continue
        if contains_blocked_days(schedule_slots, blocked_days):
            continue
        if not meets_max_days_condition(schedule_slots, max_days):
            continue

        valid_schedules.append(schedule_slots)

    return valid_schedules


#
# --- 5) Build a 'weekly grid' for one schedule ---
#
def build_week_grid(schedule_slots, start_hour=8, end_hour=18, interval=30):
    """
    Convert schedule_slots (list of (ev_name, day, start, end)) into a dictionary
    to display as a weekly table. We create half-hour blocks from start_hour to end_hour.

    Returns: {
      "days": [...],
      "time_blocks": [(480,"08:00"), (510,"08:30"), ...],
      "grid": { "Mon-480": [...event names...], ... }
    }
    """
    days_list = ["Mon", "Tue", "Wed", "Thu", "Fri"]  # or more if needed
    # Build the time blocks
    time_blocks = []
    for hour in range(start_hour, end_hour):
        for minute_offset in [0, interval]:
            block_minute = hour * 60 + minute_offset
            if block_minute >= end_hour * 60:
                break
            label = f"{block_minute // 60:02d}:{block_minute % 60:02d}"
            time_blocks.append((block_minute, label))

    # Initialize the grid
    grid = {}
    for d in days_list:
        for (block_minute, _) in time_blocks:
            key = f"{d}-{block_minute}"
            grid[key] = []

    # Fill it
    for (ev_name, ev_day, ev_start, ev_end) in schedule_slots:
        if ev_day not in days_list:
            continue
        for (block_minute, _) in time_blocks:
            block_start = block_minute
            block_end = block_minute + interval
            # Overlap check
            if (ev_start < block_end) and (ev_end > block_start):
                key = f"{ev_day}-{block_minute}"
                grid[key].append(ev_name)

    return {
        "days": days_list,
        "time_blocks": time_blocks,
        "grid": grid
    }