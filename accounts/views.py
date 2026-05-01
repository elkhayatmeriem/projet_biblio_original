from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm



def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        # 🔴 bloquer directement si le form n'est pas valide
        if not form.is_valid():
            return render(request, "accounts/register.html", {"form": form})

        # ✅ ici tout est valide
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        # check username exist
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return redirect("accounts:register")

        # create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Compte créé avec succès")
        return redirect("accounts:login")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "accounts/login.html", {
                "message": "Email not found"
            })

        auth_user = authenticate(
            request,
            username=user.username,
            password=password
        )

        if auth_user is not None:
            login(request, auth_user)
            return redirect("home")

        return render(request, "accounts/login.html", {
            "message": "Wrong password"
        })

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('accounts:login')


def profile(request):
    return render(request, "profile.html")


def emprunts(request):
    return render(request, "emprunts.html")


def penalites(request):
    return render(request, "penalites.html")



@login_required
def my_information(request):
    return render(request, "accounts/my_information.html", {
        "user": request.user
    })