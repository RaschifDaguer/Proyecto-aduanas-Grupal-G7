from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, username, email=None, credencial=None, role=None, password=None, **extra_fields):
        if not username:
            raise ValueError('El nombre de usuario es obligatorio')
        if credencial and (len(credencial) != 6 or not credencial.isdigit()):
            raise ValueError('La credencial debe ser un número de 6 dígitos')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, credencial=credencial, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email=email, password=password, role=None, credencial=None, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('gerente', 'Gerente'),
        ('despachante', 'Despachante de Aduanas'),
    )
    credencial = models.CharField(max_length=6, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.get_role_display() if self.role else 'Superusuario'})"

class HistorialBusqueda(models.Model):
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    termino = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} buscó '{self.termino}' el {self.fecha}"

class Seccion(models.Model):
    titulo = models.CharField(max_length=10, verbose_name="Título de Sección")  # Ej: 1, 2, 3...
    descripcion = models.TextField(verbose_name="Descripción")
    notas = models.TextField(verbose_name="Notas", blank=True, null=True)
    notas_complementarias_nandina = models.TextField(verbose_name="Notas Complementarias NANDINA", blank=True, null=True)

    def __str__(self):
        return f"Sección {self.titulo}"

    def notas_html(self):
        return self.notas.replace('\n', '<br>') if self.notas else ''

    def notas_nandina_html(self):
        return self.notas_complementarias_nandina.replace('\n', '<br>') if self.notas_complementarias_nandina else ''

class Capitulo(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name="capitulos")
    titulo = models.CharField(max_length=10, verbose_name="Capítulo")  # Ej: 01, 02, etc.
    descripcion = models.TextField(verbose_name="Descripción")
    nota = models.TextField(verbose_name="Nota", blank=True, null=True)

    def __str__(self):
        return f"Capítulo {self.titulo}"

    def nota_html(self):
        return self.nota.replace('\n', '<br>') if self.nota else ''

class DocumentosAdicionales(models.Model):
    tipo_doc = models.CharField(max_length=50, verbose_name="Tipo de Doc")
    entidad_emite = models.CharField(max_length=100, verbose_name="Entidad que emite")
    disp_legal = models.CharField(max_length=255, verbose_name="Disp. Legal")

    def __str__(self):
        return f"{self.tipo_doc} - {self.entidad_emite}"

class PreferenciasArancelarias(models.Model):
    can = models.CharField(max_length=50, verbose_name="CAN", blank=True, null=True)
    ace_36 = models.CharField(max_length=50, verbose_name="ACE 36", blank=True, null=True)
    ace_47 = models.CharField(max_length=50, verbose_name="ACE 47", blank=True, null=True)
    ven = models.CharField(max_length=50, verbose_name="VEN", blank=True, null=True)

    def __str__(self):
        if self.can == '100' or self.ace_36 == '100' or self.ace_47 == '100' or self.ven == '100':
            return '100'
        return ''

class ACE22(models.Model):
    chi = models.CharField(max_length=50, verbose_name="Chi", blank=True, null=True)
    prot = models.CharField(max_length=50, verbose_name="Prot", blank=True, null=True)

    def __str__(self):
        return f"Chi: {self.chi}, Prot: {self.prot}"

class ACE66Mexico(models.Model):
    ace_66_mexico = models.CharField(max_length=100, verbose_name="ACE 66 / México", blank=True, null=True)

    def __str__(self):
        return self.ace_66_mexico or ""

class Arancel(models.Model):
    # El campo 'codigo' sigue existiendo pero no se mostrará en el admin
    codigo = models.CharField(max_length=50, verbose_name="Código completo", blank=True)  # Quitar unique=True
    capituloaranc = models.ForeignKey(Capitulo, on_delete=models.CASCADE, verbose_name="Capítulo")
    partida = models.CharField(max_length=4, verbose_name="Partida", blank=True, null=True)
    subpartida = models.CharField(max_length=4, verbose_name="Subpartida", blank=True, null=True)
    subpartida_nacional = models.CharField(max_length=6, verbose_name="Subpartida Nacional", blank=True, null=True)
    desagregacion_nacional = models.CharField(max_length=10, verbose_name="Desagregación Nacional", blank=True, null=True)
    descripcion = models.CharField(max_length=255, verbose_name="Descripción de la Mercancía", blank=True, null=True)
    ga = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="GA %", blank=True, null=True)
    ice = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="ICE %", blank=True, null=True)
    unidad_medida = models.CharField(max_length=50, verbose_name="Unidad de Medida", blank=True, null=True)
    despacho_frontera = models.CharField(max_length=100, verbose_name="Despacho en Frontera", blank=True, null=True)
    documentos_adicionales = models.ForeignKey(DocumentosAdicionales, on_delete=models.SET_NULL, null=True, blank=True)
    preferencias_arancelarias = models.ForeignKey(PreferenciasArancelarias, on_delete=models.SET_NULL, null=True, blank=True)
    ace22 = models.ForeignKey(ACE22, on_delete=models.SET_NULL, null=True, blank=True)
    ace66_mexico = models.ForeignKey(ACE66Mexico, on_delete=models.SET_NULL, null=True, blank=True)
    arancel_padre = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='aranceles_hijos',
        verbose_name='Arancel padre',
        limit_choices_to={'arancel_padre__isnull': True}
    )

    class Meta:
        ordering = ['codigo']  # Solo por código, sin arancel_padre para evitar bucles

    def clean(self):
        from django.core.exceptions import ValidationError
        # Solo validar duplicados si el código NO está vacío
        if self.codigo:
            qs = Arancel.objects.filter(codigo=self.codigo)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({'codigo': 'Ya existe un arancel con este código.'})

    def save(self, *args, **kwargs):
        # Formatear el capítulo a dos dígitos para el código
        capitulo = f"{int(self.capituloaranc.titulo):02}" if self.capituloaranc and self.capituloaranc.titulo.isdigit() else (self.capituloaranc.titulo if self.capituloaranc else '')
        partida = f"{self.partida}." if self.partida else ''
        subpartida = f"{self.subpartida}." if self.subpartida else ''
        subpartida_nacional = f"{self.subpartida_nacional}." if self.subpartida_nacional else ''
        desagregacion = self.desagregacion_nacional or ''
        self.codigo = f"{capitulo}{partida}{subpartida}{subpartida_nacional}{desagregacion}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.capituloaranc} - {self.descripcion}"
