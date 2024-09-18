# urls.py
from django.urls import path
from . import views  
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
        #Para vistas basadas en clases
    #path('perfiles/', PerfilListAPIView.as_view(), name='perfil-list'),
    #path('perfiles/<int:pk>/', PerfilDetailAPIView.as_view(), name='perfil-detail'),

    #Vistas basadas en funciones
    path('me/', views.me),
    path('admin-view/', views.admin_view),
    path('perfiles/', views.perfil_list, name='perfil-list'),
    path('perfiles/<int:pk>/', views.perfil_detail, name='perfil-detail'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]