from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from products.models import Book
from accounts.models import Borrow
from .models import CartItem


# =========================
# PANIER
# =========================
def cart_view(request):

    if request.user.is_authenticated:

        items = CartItem.objects.filter(user=request.user)
        total = sum(item.quantity for item in items)

        return render(request, "cart/cart.html", {
            "cart_items": items,
            "total_items": total,
            "session_cart": False
        })

    else:

        cart = request.session.get("cart", {})
        items = list(cart.values())

        total = sum(item.get("quantity", 1) for item in items)

        return render(request, "cart/cart.html", {
            "cart_items": items,
            "total_items": total,
            "session_cart": True
        })


# =========================
# AJOUTER AU PANIER
# =========================
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

    messages.success(request, "📚 Livre ajouté au panier !")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# =========================
# SUPPRIMER DU PANIER
# =========================
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

    messages.success(request, "🗑️ Livre supprimé du panier")
    return redirect('cart')


# =========================
# EMPRUNTER (CORRIGÉ)
# =========================
@login_required
def emprunter(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    # créer emprunt
    Borrow.objects.create(
        user=request.user,
        book=item.book,
        returned=False
    )

    # rendre livre indisponible
    item.book.available = False
    item.book.save()

    # supprimer du panier
    item.delete()

    messages.success(request, "📚 Livre emprunté avec succès !")
    return redirect('cart')


# =========================
# RETOURNER LIVRE
# =========================
@login_required
def retourner(request, borrow_id):

    borrow = get_object_or_404(
        Borrow,
        id=borrow_id,
        user=request.user
    )

    borrow.returned = True
    borrow.save()

    borrow.book.available = True
    borrow.book.save()

    messages.success(request, "📚 Livre retourné avec succès !")
    return redirect('accounts:emprunts')