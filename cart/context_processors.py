from .models import CartItem

def cart_context(request):

    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
        total = sum(item.quantity for item in items)

        return {
            "cart_items": items,
            "total_items": total
        }

    else:
        cart = request.session.get("cart", {})
        items = list(cart.values())
        total = sum(item.get("quantity", 1) for item in items)

        return {
            "cart_items": items,
            "total_items": total
        }