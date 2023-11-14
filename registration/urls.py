from django.urls import path
from .views import login_page, register_page, logout_user, reset_password, new_password

urlpatterns = [
    path('login/', login_page, name="login"),
    path('signup/', register_page, name='signup'),
    path('logout/', logout_user, name="logout"),
    path('reset-password/', reset_password, name='change'),
    path('new-password/', new_password, name='new'),
]
