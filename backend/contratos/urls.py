from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardDataView, ContratoListView, ContratoDetailView,
    LineaTiempoViewSet, UbicacionViewSet, ContratistaViewSet,
    PmtResumenViewSet, InversionEjercidaViewSet, DatoGeologicoViewSet
)

router = DefaultRouter()
router.register(r'lineas-tiempo', LineaTiempoViewSet, basename='lineas-tiempo')
router.register(r'ubicaciones', UbicacionViewSet, basename='ubicaciones')
router.register(r'contratistas', ContratistaViewSet, basename='contratistas')
router.register(r'pmt', PmtResumenViewSet, basename='pmt')
router.register(r'inversiones', InversionEjercidaViewSet, basename='inversiones')
router.register(r'geologicos', DatoGeologicoViewSet, basename='geologicos')

urlpatterns = [
    path('dashboard/', DashboardDataView.as_view(), name='dashboard-data'),
    path('contracts/', ContratoListView.as_view(), name='contracts-list'),
    path('contracts/<path:pk>/', ContratoDetailView.as_view(), name='contract-detail'),
    path('', include(router.urls)),
]
