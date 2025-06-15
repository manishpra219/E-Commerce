
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="blogHome"),
    
    # blog/urls.py or wherever your blog URLs are defined
    path('blogpost/', views.blogpost, name='blogpostDefault'),
    path('blogpost/<int:id>/', views.blogpost, name='blogpostWithId'),

]
