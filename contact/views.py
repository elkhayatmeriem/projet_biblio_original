from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact

def contact_view(request):
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
        else:
            messages.error(request, "Tous les champs sont obligatoires.")

    return render(request, 'contact/contact.html')