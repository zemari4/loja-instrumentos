from . import services


def cart(request):
    return {"cart_count": services.cart_count(request.session)}
