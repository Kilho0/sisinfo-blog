from django.urls import path

from . import views

urlpatterns = [
    path('contas/cadastro/', views.SignupView.as_view(), name='signup'),
    path('perfil/', views.MyProfileView.as_view(), name='my_profile'),
    path('perfil/editar/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('usuarios/<str:username>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('acessos/', views.AccessListView.as_view(), name='access_list'),
    path('acessos/<int:pk>/', views.AccessUpdateView.as_view(), name='access_update'),
]
