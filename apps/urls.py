from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from . import views
from .api_views import TableViewSet

schema_view = get_schema_view(
   openapi.Info(
      title="Tabel API",
      default_version='v1',
      description="API dokumentasi untuk manajemen tabel",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'tables', TableViewSet, basename='api_table')

urlpatterns = [
      path('', views.login_view, name='login'),
      path('login/', views.login_view, name='login'),
      path('logout/', views.logout_view, name='logout'),
      path('register/', views.register_view, name='register'),
      path('dashboard/', views.dashboard_view, name='dashboard'),
      path('create_table/', views.create_table_view, name='create_table'),
      path('table_detail/<int:table_id>/', views.table_detail_view, name='table_detail'),
      path('add_column/<int:table_id>/', views.add_column_view, name='add_column'),
      path('add_data/<int:table_id>/', views.add_data_view, name='add_data'),
      path('edit_data/<int:row_id>/', views.edit_data_view, name='edit_data'),
      path('delete_data/<int:row_id>/', views.delete_data_view, name='delete_data'),
      path('edit_table/<int:table_id>/', views.edit_table_view, name='edit_table'),
      path('delete_table/<int:table_id>/', views.delete_table_view, name='delete_table'),
      path('api/get_columns/<int:table_id>/', views.get_columns, name='get_columns'),
      path('api/', include(router.urls)),
      re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
      path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
      path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
      path('profile/', views.profile_view, name='profile'),
      path('export_table/<int:table_id>/<str:format>/', views.export_table_data, name='export_table'),
      path('import_data/<int:table_id>/', views.import_data, name='import_data'),
      path('import_table/', views.import_table, name='import_table'),
      path('table/<int:table_id>/column/<int:column_id>/edit/', views.edit_column_view, name='edit_column'),
      path('table/<int:table_id>/column/<int:column_id>/delete/', views.delete_column_view, name='delete_column'),
]