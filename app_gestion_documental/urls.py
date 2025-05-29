from django.urls import path
from .views import TextExtractionView

urlpatterns = [
    path('extraer-texto/', TextExtractionView.as_view(), name='extraer_texto'),
]
