from django.urls import path
from  .views import *

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('create-company/', CreateCompanyView.as_view(), name='create_company'),
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/update/<int:id>/', CompanyUpdateView.as_view(), name='company-update'),
    path('company/<int:id>/change-status/', ChangeCompanyStatusView.as_view(), name='change-company-status'),
    path('company/<int:id>/delete/', DeleteCompanyView.as_view(), name='delete-company'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('companies/<int:id>/', SingleCompanyListView.as_view(), name='company-list'),
    path('companies/count/', CompanyCountView.as_view(), name='company-count'),
]

