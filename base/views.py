from django.shortcuts import render,redirect
from django.contrib import messages
from contact.models import Contact   

def home(request):
    return render(request, 'base/home.html')

def contact(request):
    return render(request, 'contact.html')


def home(request):
    
    return render(request, 'base/home.html')

def contact(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if nom and email and message:
            Contact.objects.create(
                nom=nom,
                email=email,
                message=message
            )
            messages.success(request, "Message envoyé avec succès !")
            return redirect('contact')

    return render(request, 'contact/contact.html')