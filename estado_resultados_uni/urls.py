from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('resumen.urls')),
    path('', TemplateView.as_view(template_name='resumen/inicio.html'), name='inicio'),
]
