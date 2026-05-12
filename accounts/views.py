from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone

from .forms import RegisterForm, EditProfileForm
from django.contrib.auth.forms import UserChangeForm

from .models import Borrow   # ✅ AJOUT IMPORTANT


# -------------------------
# REGISTER
# -------------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if not form.is_valid():
            print(form.errors)
            return render(request, "accounts/register.html", {"form": form})

        first_name = form.cleaned_data.get("first_name")
        last_name = form.cleaned_data.get("last_name")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        username = email

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

    return render(request, "accounts/register.html", {"form": RegisterForm()})


# -------------------------
# LOGIN
# -------------------------
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

        auth_user = authenticate(request, username=user.username, password=password)

        if auth_user is not None:

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


# -------------------------
# LOGOUT
# -------------------------
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('accounts:login')


# -------------------------
# PROFILE (optionnel)
# -------------------------
def profile(request):
    return render(request, "profile.html")


# -------------------------
# PÉNALITÉ CALCUL
# -------------------------
def calculate_penalty(borrow):
    days = (timezone.now() - borrow.borrowed_at).days
    if days > 7:
        return (days - 7) * 2
    return 0


# -------------------------
# MES EMPRUNTS
# -------------------------
@login_required
def emprunts(request):

    borrows = Borrow.objects.filter(
        user=request.user
    ).order_by('-borrowed_at')

    return render(request, "accounts/emprunts.html", {
        "borrows": borrows
    })

# -------------------------
# MES PÉNALITÉS
# -------------------------
@login_required
def penalites(request):
    borrows = Borrow.objects.filter(
        user=request.user,
        sanction_applied=True
    ).order_by('-borrowed_at')

    return render(request, "accounts/penalites.html", {
        "borrows": borrows
    })


# -------------------------
# MES INFOS
# -------------------------
@login_required
def my_information(request):
    if request.user.is_staff:
        return redirect('/admin/')

    return render(request, "accounts/my_information.html", {
        "user": request.user
    })


# -------------------------
# CHANGE PASSWORD
# -------------------------
@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        new_password2 = request.POST.get("new_password2")

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, "Ancien mot de passe incorrect")
            return redirect("accounts:change_password")

        if new_password != new_password2:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return redirect("accounts:change_password")

        user.set_password(new_password)
        user.save()

        logout(request)

        messages.success(request, "Mot de passe modifié avec succès")
        return redirect("accounts:login")

    return render(request, "accounts/change_password.html")


# -------------------------
# EDIT PROFILE
# -------------------------
@login_required
def edit_information(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()

            messages.success(request, "Informations mises à jour avec succès")
            return redirect("accounts:my_information")

    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "accounts/edit_information.html", {
        "form": form
    })