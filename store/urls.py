from django.urls import path
from store.views import cart, checkout, order, \
    logout, show_product_details,add_to_cart, validate_payment
from store.views import Signup, Login, Index
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('cart/', cart, name='cart'),
    path('order/', order, name='order'),
    path('login', Login.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('signup',  Signup.as_view(), name='signup'),
    path('checkout',  checkout, name='checkout'),
    path('validate_payment', validate_payment, name='validate_payment'),
    path('product_id/<str:slug>', show_product_details, name='show_product_details'),
    path('add_to_cart/<str:slug>/<str:size>', add_to_cart,name='add_to_cart'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)