from django.urls import path
from app_placas import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    #para criar uma rota use nome da rota, view responsavel, nome referencia
    path('',views.home, name='home'),
    path('camera', views.camera, name='camera'),
    path('admin/', admin.site.urls)
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)