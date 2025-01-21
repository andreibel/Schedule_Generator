from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Schedule, Event
from django.core.exceptions import ValidationError

def index(request):
    last_schedules = Schedule.objects.order_by('-created_at')[:5]
    context = {'last_schedules': last_schedules}
    return render(request, 'Generator/index.html', context)
# Create your views here.
def detail(request,request_id):
    schedule = get_object_or_404(Schedule, pk=request_id)
    return render(request,'Generator/details.html', {'schedule':schedule})

def events(request,request_id):
    schedule = get_object_or_404(Schedule, pk=request_id)
    try:
        e = Event(name=request.POST["event_name"], schedule=schedule,time_slots=request.POST["event_time_slot"])
        e.clean()
        e.save()
    except KeyError:
        return HttpResponse(f"error {schedule.name}")
    else:
        return HttpResponse(f"thanks you to save another event in {schedule.name}")

