from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('Generator:index')  # Adjust URL name if needed
    else:
        form = UserCreationForm()
    return render(request, 'Accounts/signup.html', {'form': form})