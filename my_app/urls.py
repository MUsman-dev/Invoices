from django.urls import path
from . import views

urlpatterns = [
    path('invoices/', views.InvoiceListView.as_view(), name='invoices-list'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoices-detail'),
]