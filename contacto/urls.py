from django.urls import path
from .views import contacto_page

urlpatterns = [
    path('contacto', contacto_page, name="contacto"),    
]