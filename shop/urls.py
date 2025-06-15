
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("handlerequest/", views.handlerequest, name="HandleRequest"),
    path("tracker/", views.tracker, name="Tracker"),
    path('terms/', views.terms, name='terms'),
    path('refund/', views.refund, name='refund'),
    path('shipping/', views.shipping, name='shipping'),
    path('privacy/', views.privacy, name='privacy'),
    path('contact_policy/', views.contact_policy, name='contact_policy'),
]
 
    
    
    
    