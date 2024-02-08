"""
URL configuration for django_consumer_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from consumers.views import ConsumerListView
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Django Consumer API",
        default_version='v1',
        description="API to filter consumers from provided data by CSV",
        contact=openapi.Contact(email="spiderhc@gmail.com"),
    ),
    public=True,
)

urlpatterns = [
    path('consumers/', ConsumerListView.as_view(), name='consumer-list'),
    path('consumers/import-csv/', ConsumerListView.import_data_from_csv, name='import-csv'), 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]