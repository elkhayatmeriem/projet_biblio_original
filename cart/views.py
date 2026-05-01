from django.shortcuts import render
def cart_view(request):
    cart = request.session.get("cart", {})

    items = []
    total = 0

    for book_id, item in cart.items():
        items.append(item)
        total += item.get("quantity", 1)

    return render(request, "cart/cart.html", {
        "cart_items": items,
        "total_items": total
    })