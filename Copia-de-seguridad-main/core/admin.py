from django.contrib import admin
from .models import Seccion, Capitulo, DocumentosAdicionales, PreferenciasArancelarias, ACE22, ACE66Mexico, Arancel, CustomUser

class ArancelHijoInline(admin.TabularInline):
    model = Arancel
    fk_name = 'arancel_padre'
    extra = 1
    verbose_name = 'Arancel hijo'
    verbose_name_plural = 'Aranceles hijos'

@admin.register(Arancel)
class ArancelAdmin(admin.ModelAdmin):
    exclude = ('codigo',)
    inlines = [ArancelHijoInline]
    ordering = ('arancel_padre', 'codigo')  # Ordena padres primero, luego hijos, ambos por código ascendente

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'credencial', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'credencial')
    exclude = ()
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Información de usuario', {'fields': ('credencial', 'role')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'credencial', 'role', 'is_staff', 'is_superuser'),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # El superusuario ve todo, los demás solo ven despachantes
        if not request.user.is_superuser:
            return qs.filter(role='despachante')
        return qs

    def has_delete_permission(self, request, obj=None):
        # Solo el superusuario puede eliminar gerentes
        if obj and obj.role == 'gerente' and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        # Solo el superusuario puede editar gerentes
        if obj and obj.role == 'gerente' and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        # El gerente no puede cambiar su propio rol ni credencial
        ro = list(super().get_readonly_fields(request, obj))
        if obj and obj.role == 'gerente' and not request.user.is_superuser:
            ro += ['role', 'credencial']
        return ro

admin.site.register(Seccion)
admin.site.register(Capitulo)
admin.site.register(DocumentosAdicionales)
admin.site.register(PreferenciasArancelarias)
admin.site.register(ACE22)
admin.site.register(ACE66Mexico)
