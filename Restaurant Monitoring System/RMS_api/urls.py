from django.urls import path
from .views import TriggerReportView, GetReportView

urlpatterns = [
    path('trigger-report/', TriggerReportView.as_view(), name='trigger-report'),
    path('get-report/', GetReportView.as_view(), name='get-report'),
]
