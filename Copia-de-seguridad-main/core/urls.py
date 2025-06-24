from django.urls import path
from .views import busqueda_view, busqueda_avanzada, autocompletar_arancel, busqueda_codigo, busqueda_descripcion, autocompletar_codigo, autocompletar_descripcion, busqueda_combinada, login_view, logout_view
from .views import (
    ajax_buscar_empleados, ajax_tabla_empleados, ajax_form_empleado,
    ajax_lista_usuarios, ajax_tabla_historial,
    ajax_buscar_aranceles, ajax_tabla_aranceles, ajax_form_arancel,
)
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('busqueda/', busqueda_view, name='busqueda'),
    path('busqueda-avanzada/', busqueda_avanzada, name='busqueda_avanzada'),
    path('autocompletar-arancel/', autocompletar_arancel, name='autocompletar_arancel'),
    path('busqueda-codigo/', busqueda_codigo, name='busqueda_codigo'),
    path('busqueda-descripcion/', busqueda_descripcion, name='busqueda_descripcion'),
    path('autocompletar-codigo/', autocompletar_codigo, name='autocompletar_codigo'),
    path('autocompletar-descripcion/', autocompletar_descripcion, name='autocompletar_descripcion'),
    path('busqueda-combinada/', busqueda_combinada, name='busqueda_combinada'),
    path('aranceles/', views.aranceles_panel, name='aranceles'),
    path('aranceles/create/', views.arancel_create, name='arancel_create'),
    path('aranceles/<int:pk>/edit/', views.arancel_edit, name='arancel_edit'),
    path('aranceles/<int:pk>/delete/', views.arancel_delete, name='arancel_delete'),
    path('aranceles/form/', views.arancel_form, name='arancel_form'),
    path('aranceles/<int:pk>/form/', views.arancel_form, name='arancel_form_edit'),
    path('despachantes/', views.despachantes_panel, name='despachantes_panel'),
    path('despachantes/create/', views.despachante_create, name='despachante_create'),
    path('despachantes/<int:pk>/delete/', views.despachante_delete, name='despachante_delete'),
    path('despachantes/<int:pk>/form/', views.despachante_form, name='despachante_form'),
    path('despachantes/<int:pk>/edit/', views.despachante_edit, name='despachante_edit'),
    path('historial/', views.historial_panel, name='historial_panel'),
    path('ajax/buscar_empleados/', ajax_buscar_empleados, name='ajax_buscar_empleados'),
    path('ajax/tabla_empleados/', ajax_tabla_empleados, name='ajax_tabla_empleados'),
    path('ajax/form_empleado/', ajax_form_empleado, name='ajax_form_empleado'),
    path('ajax/form_empleado/<int:pk>/', ajax_form_empleado, name='ajax_form_empleado_edit'),
    path('ajax/lista_usuarios/', ajax_lista_usuarios, name='ajax_lista_usuarios'),
    path('ajax/tabla_historial/', ajax_tabla_historial, name='ajax_tabla_historial'),
    path('ajax/buscar_aranceles/', ajax_buscar_aranceles, name='ajax_buscar_aranceles'),
    path('ajax/tabla_aranceles/', ajax_tabla_aranceles, name='ajax_tabla_aranceles'),
    path('ajax/form_arancel/', ajax_form_arancel, name='ajax_form_arancel'),
    path('ajax/form_arancel/<int:pk>/', ajax_form_arancel, name='ajax_form_arancel_edit'),
    path('panel-gerente/', views.gerente_panel, name='panel_gerente'),
    path('ajax/form_seccion/', views.ajax_form_seccion, name='ajax_form_seccion'),
    path('ajax/form_capitulo/', views.ajax_form_capitulo, name='ajax_form_capitulo'),
    path('ajax/sugerencias_historial/', views.sugerencias_historial, name='sugerencias_historial'),
]

