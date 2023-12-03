from django.urls import path
from app_placas import views

urlpatterns = [
    #para criar uma rota use nome da rota, view responsavel, nome referencia
    path('',views.home, name='home'),
    path('camera', views.camera, name='camera')
]
