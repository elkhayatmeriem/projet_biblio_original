from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import EditProfileForm
from django.contrib.auth.forms import UserChangeForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if not form.is_valid():
            print(form.errors)  # 🔥 IMPORTANT DEBUG
            return render(request, "accounts/register.html", {"form": form})

        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        username = email  # simple login

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email existe déjà.")
            return redirect("accounts:register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
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

            # BLOCK ADMIN/STAFF FROM USER LOGIN
            if auth_user.is_staff or auth_user.is_superuser:
                return render(request, "accounts/login.html", {
                    "message": "Admins must log in via admin panel."
                })

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
    if request.user.is_staff:
        return redirect('/admin/')

    return render(request, "accounts/my_information.html", {
        "user": request.user
    })



@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        new_password2 = request.POST.get("new_password2")

        user = request.user

        # 1. CHECK OLD PASSWORD (IMPORTANT)
        if not user.check_password(old_password):
            messages.error(request, "Ancien mot de passe incorrect")
            return redirect("accounts:change_password")

        # 2. CHECK MATCH NEW PASSWORDS
        if new_password != new_password2:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return redirect("accounts:change_password")

        # 3. SAVE NEW PASSWORD
        user.set_password(new_password)
        user.save()

        # 4. IMPORTANT: logout after password change
        logout(request)

        messages.success(request, "Mot de passe modifié avec succès")
        return redirect("accounts:login")

    return render(request, "accounts/change_password.html")

@login_required
def edit_information(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save(commit=False)

            #  IMPORTANT : sync username avec email
            user.username = user.email

            user.save()

            messages.success(request, "Informations mises à jour avec succès")
            return redirect("accounts:my_information")
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "accounts/edit_information.html", {
        "form": form
    })
