from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from products.models import Book
from accounts.models import Borrow
from .models import CartItem


def cart_view(request):

    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
        total = sum(item.quantity for item in items)

        return render(request, "cart/cart.html", {
            "cart_items": items,
            "total_items": total,
            "session_cart": False
        })

    cart = request.session.get("cart", {})
    items = list(cart.values())
    total = sum(item.get("quantity", 1) for item in items)

    return render(request, "cart/cart.html", {
        "cart_items": items,
        "total_items": total,
        "session_cart": True
    })


def add_to_cart(request, book_id):

    book = get_object_or_404(Book, id=book_id)

    if request.user.is_authenticated:

        item, created = CartItem.objects.get_or_create(
            user=request.user,
            book=book
        )

        if not created:
            item.quantity += 1
        else:
            item.quantity = 1

        item.save()

    else:

        cart = request.session.get("cart", {})
        book_id_str = str(book.id)

        if book_id_str in cart:
            cart[book_id_str]["quantity"] += 1
        else:
            cart[book_id_str] = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "quantity": 1
            }

        request.session["cart"] = cart
        request.session.modified = True

    messages.success(request, "Livre ajouté au panier")
    return redirect(request.META.get("HTTP_REFERER", "home"))


def remove_from_cart(request, item_id):

    if request.user.is_authenticated:

        item = get_object_or_404(
            CartItem,
            id=item_id,
            user=request.user
        )
        item.delete()

    else:

        cart = request.session.get("cart", {})
        cart.pop(str(item_id), None)

        request.session["cart"] = cart
        request.session.modified = True

    messages.success(request, "Livre supprimé")
    return redirect("cart")


@login_required
def emprunter(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    book = item.book

    if not book.available:
        messages.error(request, "Livre indisponible")
        return redirect("cart")

    blocked = Borrow.objects.filter(
        user=request.user,
        blocked_until__gt=timezone.now()
    ).first()

    if blocked:
        messages.error(
            request,
            f"Compte bloqué jusqu'au {blocked.blocked_until.strftime('%d/%m/%Y %H:%M')}"
        )
        return redirect("accounts:emprunts")

    Borrow.objects.create(
        user=request.user,
        book=book
    )

    book.available = False
    book.save()

    item.delete()

    messages.success(request, "Livre emprunté avec succès")
    return redirect("accounts:emprunts")


@login_required
def retourner(request, borrow_id):

    borrow = get_object_or_404(
        Borrow,
        id=borrow_id,
        user=request.user
    )

    if borrow.returned:
        messages.warning(request, "Livre déjà retourné")
        return redirect("accounts:emprunts")

    borrow.returned = True
    borrow.returned_at = timezone.now()

    days = (borrow.returned_at - borrow.borrowed_at).days

    if days > 7:
        retard = days - 7

        borrow.blocked_days = retard * 2
        borrow.blocked_until = timezone.now() + timedelta(days=borrow.blocked_days)
        borrow.sanction_applied = True
        borrow.notification = f"Retard détecté : compte bloqué {borrow.blocked_days} jours."

        messages.error(
            request,
            f"Retard détecté. Votre compte est bloqué pendant {borrow.blocked_days} jours."
        )

    else:
        borrow.notification = "Retour validé avec succès"
        messages.success(request, "Retour validé avec succès")

    borrow.save()

    if borrow.book:
        borrow.book.available = True
        borrow.book.save()

    return redirect("accounts:emprunts")