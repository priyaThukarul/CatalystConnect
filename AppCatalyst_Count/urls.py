from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('logout/', logout_view, name='logout_view'),
    path('base/', base, name='base'),
    path('upload_data/', upload_data, name='upload_data'),
    path('query_data/', QueryBuilderView.as_view(), name='query_data'),
    path('users/', users, name='users'),
    path('upload/', ChunkedUploadView.as_view(), name='api_chunked_upload'),
    path('api/company-count/', CompanyCountView.as_view(), name='company-count'),
    path('dynamic_fields/', DynamicFieldsView.as_view(), name='dynamic_fields'),
    
]
