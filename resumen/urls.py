from django.urls import path
from . import views

urlpatterns = [
    path('', views.estado_resultados, name='estado_resultados'),
    path('subir/', views.subir_excel, name='subir_excel'),
    path('clasificacion/', views.clasificacion, name='clasificacion'),
    path('reporte/', views.generar_reporte, name='generar_reporte'),
    path('estado_resultados/', views.estado_resultados, name='estado_resultados'),
    path('resumen_general/', views.resumen_general, name='resumen_general'),
    path('descargar_resumen_excel/', views.descargar_resumen_excel, name='descargar_resumen_excel'),
    path('descargar_resumen_pdf/', views.descargar_resumen_pdf, name='descargar_resumen_pdf'),
    path('descargar_plantilla/', views.descargar_plantilla, name='descargar_plantilla'),
]
