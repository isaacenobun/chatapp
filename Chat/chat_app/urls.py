from django.urls import path
from . import views

urlpatterns = [
    path('sign-in/', views.sign_in, name='sign-in'),
    path('sign-out/', views.sign_out, name='sign-out'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('chat/', views.main, name='main'),
    path('stream/', views.chat_stream, name='stream'),
    path('send/', views.send, name='send'),
    
]
