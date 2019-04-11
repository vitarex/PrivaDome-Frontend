""" API endpoints URL. """
from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from . import views

SCHEMA_VIEW = get_schema_view(title='API')

ROUTER = DefaultRouter()
ROUTER.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^schema/$', SCHEMA_VIEW),
    url(r'^', include(ROUTER.urls))
]

urlpatterns += [
    url(r'login/', views.ObtainExpiringAuthToken.as_view(), name='login')
]

urlpatterns += [
    url(r'tiles/data/', views.tiles_data)
]

urlpatterns += [
    url(r'modules/config/', views.module_config, name='module_config')
]

urlpatterns += [
    url(r'modules/info/', views.module_schema, name='module_schema')
]

urlpatterns += [
    url(r'modules/addpolicy/group/', views.add_policy_group, name='add_policy_group')
]

urlpatterns += [
    url(r'modules/addpolicy/address/', views.add_policy_address, name='add_policy_address')
]

urlpatterns += [
    url(r'modules/deletepolicy/group/', views.delete_policy_group, name='delete_policy_group')
]

urlpatterns += [
    url(r'modules/deletepolicy/address/', views.delete_policy_address, name='delete_policy_address')
]

urlpatterns += [
    url(r'modules/updatepolicy/network/', views.update_policy_network, name='update_policy_network')
]

urlpatterns += [
    url(r'modules/updatepolicy/group/', views.update_policy_group, name='update_policy_group')
]

urlpatterns += [
    url(r'modules/updatepolicy/address/', views.update_policy_address, name='update_policy_address')
]

urlpatterns += [
    url(r'proctest/', views.api_procbridge_test, name='proctest')
]
