from django.urls import path
 # Import views from the accounts app
from django.contrib.auth.views import LoginView
from .views import SignoutView,SignInView


urlpatterns = [
    # path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', SignoutView.as_view(), name='logout'),
    path('login/',SignInView.as_view(),name='login'),
]