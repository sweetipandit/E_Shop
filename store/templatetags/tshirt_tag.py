from django import template
from math import floor

register = template.Library()

@register.filter
def rupee(number):
    return f'₹ {number}'


@register.filter
def total_payable_amount(cart):
    total=0
    for cart_obj in cart:
        discount = cart_obj.get('tshirt').descount
        price = cart_obj.get('size').prize
        quantity = cart_obj.get('quantity')
        sale_prices = sale_price(price, discount)
        total_of_single_product= price_quantity_multiply(sale_prices,quantity)
        total = total + total_of_single_product
    return total

@register.simple_tag
def min_price(product):
    size = product.sizevariant_set.all().order_by('prize').first()
    return size.prize

@register.simple_tag
def discount_price(product):
    price = min_price(product)
    discount = floor(price - (price * (product.descount / 100)))
    return discount

@register.simple_tag
def get_active_button_size(active_size,size):
    if active_size == size:
        return "dark"

    return "light"

@register.simple_tag
def price_quantity_multiply(sale_prices,quantity):
    return sale_prices*quantity


@register.simple_tag
def sale_price(price,discount):
    return floor(price - (price * (discount / 100)))


@register.simple_tag
def badge_class_attr(status):
    if status=="PLACED":
        return "warning"
    elif status=="COMPLETED":
        return "success"
    elif status=="CANCELED":
        return "danger"
    else:
        return "info"


@register.simple_tag
def selected_attr(request_slug,slug):
    if request_slug==slug:
        return "selected"


