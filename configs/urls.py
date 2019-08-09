from django.urls import path

from .views import IndexView, ConnectionPackCreateView, ConnectionPackLookupView

app_name = 'configs'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('generate', ConnectionPackCreateView.as_view(), name='generate'),
    path('lookup', ConnectionPackLookupView.as_view(), name='lookup'),
]
