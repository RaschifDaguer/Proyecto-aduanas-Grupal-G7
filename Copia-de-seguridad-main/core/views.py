from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm, DespachanteForm, ArancelForm, SeccionForm, CapituloForm
from .models import Seccion, Capitulo, Arancel, HistorialBusqueda, CustomUser
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string
import re
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'gerente':
            return redirect('panel_gerente')
        elif request.user.role == 'despachante':
            return redirect('busqueda')
    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            credencial = form.cleaned_data['credencial'].strip()
            try:
                user = CustomUser.objects.get(username=username, credencial=credencial)
            except CustomUser.DoesNotExist:
                user = None
            if user is not None and user.is_active:
                # Refuerza el rol y permisos para gerentes
                if user.role == 'gerente' and not user.is_staff:
                    user.is_staff = True
                    user.save()
                login(request, user)
                if user.role == 'gerente':
                    return redirect('panel_gerente')
                elif user.role == 'despachante':
                    return redirect('busqueda')
                else:
                    error = 'Usuario sin rol asignado. Contacte al administrador.'
            else:
                error = 'Credenciales incorrectas, usuario inactivo o sin permisos.'
        else:
            error = 'Formulario inválido. Revisa los datos ingresados.'
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form, 'error': error})

def logout_view(request):
    # Solo cierra la sesión del usuario, no destruye toda la sesión
    logout(request)
    # Redirige al login y evita caché
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def buscador_aranceles(request):
    capitulo = request.GET.get('capitulo')
    partida = request.GET.get('partida')
    subpartida = request.GET.get('subpartida')
    tarifa = request.GET.get('tarifa')

    aranceles = Arancel.objects.all()

    if capitulo:
        aranceles = aranceles.filter(capitulo=capitulo)
    if partida:
        aranceles = aranceles.filter(partida=partida)
    if subpartida:
        aranceles = aranceles.filter(subpartida=subpartida)
    if tarifa:
        aranceles = aranceles.filter(tarifa=tarifa)

    capitulos = Arancel.objects.values_list('capitulo', flat=True).distinct()
    partidas = aranceles.values_list('partida', flat=True).distinct()
    subpartidas = aranceles.values_list('subpartida', flat=True).distinct()
    tarifas = aranceles.values_list('tarifa', flat=True).distinct()

    secciones = Seccion.objects.all()

    return render(request, 'core/Buscadoraduanas.html', {
        'aranceles': aranceles,
        'capitulos': capitulos,
        'partidas': partidas,
        'subpartidas': subpartidas,
        'tarifas': tarifas,
        'filtro': {
            'capitulo': capitulo,
            'partida': partida,
            'subpartida': subpartida,
            'tarifa': tarifa,
        },
        'secciones': secciones,
    })

def gerente_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'gerente':
            if request.user.role == 'despachante':
                return redirect('busqueda')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def despachante_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'despachante':
            if request.user.role == 'gerente':
                return redirect('aranceles')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@despachante_required
def busqueda_view(request):
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    aranceles_qs = Arancel.objects.all()
    aranceles = aranceles_jerarquicos(aranceles_qs)
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
    })

def busqueda_avanzada(request):
    query = request.GET.get('q', '').strip()
    aranceles = Arancel.objects.all()
    resultados = []
    mensaje = ''
    if query:
        # Buscar por código (en todos los campos relevantes) o descripción
        aranceles = aranceles.filter(
            Q(codigo__icontains=query) |
            Q(capituloaranc__titulo__icontains=query) |
            Q(partida__icontains=query) |
            Q(subpartida__icontains=query) |
            Q(subpartida_nacional__icontains=query) |
            Q(desagregacion_nacional__icontains=query) |
            Q(descripcion__icontains=query)
        ).distinct()
        if not aranceles.exists():
            mensaje = 'Arancel de producto no encontrado'
        # Guardar historial si es despachante
        if request.user.is_authenticated and request.user.role == 'despachante':
            HistorialBusqueda.objects.create(usuario=request.user, termino=query)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
        'busqueda_query': query,
        'busqueda_mensaje': mensaje,
    })

def busqueda_codigo(request):
    query = request.GET.get('codigo', '').strip()
    aranceles = Arancel.objects.all()
    mensaje = ''
    if query:
        aranceles = aranceles.filter(
            Q(codigo__icontains=query) |
            Q(capituloaranc__titulo__icontains=query) |
            Q(partida__icontains=query) |
            Q(subpartida__icontains=query) |
            Q(subpartida_nacional__icontains=query) |
            Q(desagregacion_nacional__icontains=query)
        ).distinct()
        if not aranceles.exists():
            mensaje = 'Arancel de producto no encontrado por código'
        # Guardar historial si es despachante
        if request.user.is_authenticated and request.user.role == 'despachante':
            HistorialBusqueda.objects.create(usuario=request.user, termino=query)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
        'busqueda_codigo': query,
        'busqueda_codigo_mensaje': mensaje,
    })

def busqueda_descripcion(request):
    query = request.GET.get('descripcion', '').strip()
    aranceles = Arancel.objects.all()
    mensaje = ''
    if query:
        aranceles = aranceles.filter(
            Q(descripcion__icontains=query)
        ).distinct()
        if not aranceles.exists():
            mensaje = 'Arancel de producto no encontrado por descripción'
        # Guardar historial si es despachante
        if request.user.is_authenticated and request.user.role == 'despachante':
            HistorialBusqueda.objects.create(usuario=request.user, termino=query)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': aranceles,
        'busqueda_descripcion': query,
        'busqueda_descripcion_mensaje': mensaje,
    })

def autocompletar_arancel(request):
    term = request.GET.get('term', '').strip()
    sugerencias = []
    if term:
        aranceles = Arancel.objects.filter(
            Q(codigo__icontains=term) |
            Q(capituloaranc__titulo__icontains=term) |
            Q(partida__icontains=term) |
            Q(subpartida__icontains=term) |
            Q(subpartida_nacional__icontains=term) |
            Q(desagregacion_nacional__icontains=term) |
            Q(descripcion__icontains=term)
        ).distinct()[:10]
        for a in aranceles:
            sugerencias.append({
                'id': a.id,
                'codigo': a.codigo,
                'descripcion': a.descripcion,
            })
    return JsonResponse(sugerencias, safe=False)

def autocompletar_codigo(request):
    term = request.GET.get('term', '').strip()
    sugerencias = []
    if term:
        aranceles = Arancel.objects.filter(
            Q(codigo__icontains=term) |
            Q(capituloaranc__titulo__icontains=term) |
            Q(partida__icontains=term) |
            Q(subpartida__icontains=term) |
            Q(subpartida_nacional__icontains=term) |
            Q(desagregacion_nacional__icontains=term)
        ).distinct()[:10]
        for a in aranceles:
            sugerencias.append({
                'id': a.id,
                'codigo': a.codigo,
                'descripcion': a.descripcion,
                'ga': str(a.ga) if a.ga is not None else '',
                'ice': str(a.ice) if a.ice is not None else '',
                'unidad_medida': a.unidad_medida or '',
                'despacho_frontera': a.despacho_frontera or ''
            })
    if not sugerencias:
        sugerencias.append({'codigo': '', 'descripcion': 'No hay coincidencias', 'ga': '', 'ice': '', 'unidad_medida': '', 'despacho_frontera': ''})
    return JsonResponse(sugerencias, safe=False)

def autocompletar_descripcion(request):
    term = request.GET.get('term', '').strip()
    sugerencias = []
    if term:
        aranceles = Arancel.objects.filter(
            Q(descripcion__icontains=term)
        ).distinct()[:10]
        for a in aranceles:
            sugerencias.append({
                'id': a.id,
                'codigo': a.codigo,
                'descripcion': a.descripcion,
                'ga': str(a.ga) if a.ga is not None else '',
                'ice': str(a.ice) if a.ice is not None else '',
                'unidad_medida': a.unidad_medida or '',
                'despacho_frontera': a.despacho_frontera or ''
            })
    if not sugerencias:
        sugerencias.append({'codigo': '', 'descripcion': 'No hay coincidencias', 'ga': '', 'ice': '', 'unidad_medida': '', 'despacho_frontera': ''})
    return JsonResponse(sugerencias, safe=False)

def busqueda_combinada(request):
    codigo = request.GET.get('codigo', '').strip()
    descripcion = request.GET.get('descripcion', '').strip()
    mensaje = ''
    resultado = []
    aranceles_ids = set()
    def resaltar(texto, termino):
        if not texto or not termino:
            return texto or ''
        try:
            return re.sub(f'({re.escape(termino)})', r'<mark>\1</mark>', texto, flags=re.IGNORECASE)
        except Exception:
            return texto
    if codigo or descripcion:
        aranceles = Arancel.objects.all()
        if codigo:
            aranceles = aranceles.filter(
                Q(codigo__icontains=codigo) |
                Q(capituloaranc__titulo__icontains=codigo) |
                Q(partida__icontains=codigo) |
                Q(subpartida__icontains=codigo) |
                Q(subpartida_nacional__icontains=codigo) |
                Q(desagregacion_nacional__icontains=codigo)
            )
        if descripcion:
            aranceles = aranceles.filter(Q(descripcion__icontains=descripcion))
        aranceles = aranceles.distinct()
        # NUEVO: Si hay resultados, buscar todos los aranceles con el mismo capitulo y partida
        cap_partidas = set()
        for a in aranceles:
            cap = a.capituloaranc_id
            part = a.partida
            if cap and part:
                cap_partidas.add((cap, part))
        if cap_partidas:
            q = Q()
            for cap, part in cap_partidas:
                q |= Q(capituloaranc_id=cap, partida=part)
            aranceles = Arancel.objects.filter(q).order_by('codigo').distinct()
        # ...lógica de jerarquía y resaltado...
        for arancel in aranceles:
            if arancel.arancel_padre:
                padre = arancel.arancel_padre
                if padre.id not in aranceles_ids:
                    padre.codigo_resaltado = resaltar(padre.codigo, codigo)
                    padre.descripcion_resaltada = resaltar(padre.descripcion, descripcion)
                    resultado.append(padre)
                    aranceles_ids.add(padre.id)
                for hijo in padre.aranceles_hijos.all():
                    if hijo.id not in aranceles_ids:
                        hijo.codigo_resaltado = ''
                        hijo.descripcion_resaltada = resaltar(hijo.descripcion, descripcion)
                        resultado.append(hijo)
                        aranceles_ids.add(hijo.id)
            else:
                if arancel.id not in aranceles_ids:
                    arancel.codigo_resaltado = resaltar(arancel.codigo, codigo)
                    arancel.descripcion_resaltada = resaltar(arancel.descripcion, descripcion)
                    resultado.append(arancel)
                    aranceles_ids.add(arancel.id)
                for hijo in arancel.aranceles_hijos.all():
                    if hijo.id not in aranceles_ids:
                        hijo.codigo_resaltado = ''
                        hijo.descripcion_resaltada = resaltar(hijo.descripcion, descripcion)
                        resultado.append(hijo)
                        aranceles_ids.add(hijo.id)
        if not resultado:
            mensaje = 'Arancel de producto no encontrado'
    else:
        for arancel in Arancel.objects.filter(arancel_padre__isnull=True):
            arancel.codigo_resaltado = arancel.codigo
            arancel.descripcion_resaltada = arancel.descripcion
            resultado.append(arancel)
            for hijo in arancel.aranceles_hijos.all():
                hijo.codigo_resaltado = ''
                hijo.descripcion_resaltada = hijo.descripcion
                resultado.append(hijo)
    # Guardar historial si es despachante
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'despachante':
        termino = f"{codigo} {descripcion}".strip()
        if termino:
            HistorialBusqueda.objects.create(usuario=request.user, termino=termino)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    return render(request, 'core/Buscadoraduanas.html', {
        'secciones': secciones,
        'capitulos': capitulos,
        'aranceles': resultado,
        'busqueda_codigo': codigo,
        'busqueda_descripcion': descripcion,
        'busqueda_mensaje': mensaje,
    })

@gerente_required
def aranceles_panel(request):
    aranceles_qs = Arancel.objects.select_related('capituloaranc').all()
    aranceles = aranceles_jerarquicos(aranceles_qs)
    form = ArancelForm()
    return render(request, 'core/aranceles.html', {'aranceles': aranceles, 'form': form})

@gerente_required
@require_POST
def arancel_create(request):
    form = ArancelForm(request.POST)
    if form.is_valid():
        arancel = form.save()
        html = render_to_string('core/partials/arancel_row.html', {'arancel': arancel})
        return JsonResponse({'success': True, 'html': html, 'message': 'Arancel creado correctamente.'})
    # Mostrar todos los errores, incluyendo duplicados
    error_list = []
    for field, errors in form.errors.items():
        for error in errors:
            error_list.append(f"{form.fields.get(field).label if field in form.fields else field}: {error}")
    if form.non_field_errors():
        error_list += [str(e) for e in form.non_field_errors()]
    return JsonResponse({'success': False, 'errors': error_list})

@gerente_required
@require_POST
def arancel_edit(request, pk):
    arancel = Arancel.objects.get(pk=pk)
    form = ArancelForm(request.POST, instance=arancel)
    if form.is_valid():
        arancel = form.save()
        html = render_to_string('core/partials/arancel_row.html', {'arancel': arancel})
        return JsonResponse({'success': True, 'html': html, 'message': 'Arancel editado correctamente.'})
    error_list = []
    for field, errors in form.errors.items():
        for error in errors:
            error_list.append(f"{form.fields.get(field).label if field in form.fields else field}: {error}")
    if form.non_field_errors():
        error_list += [str(e) for e in form.non_field_errors()]
    return JsonResponse({'success': False, 'errors': error_list})

@gerente_required
@require_POST
def arancel_delete(request, pk):
    arancel = Arancel.objects.get(pk=pk)
    arancel.delete()
    return JsonResponse({'success': True})

@gerente_required
@require_GET
def arancel_form(request, pk=None):
    if pk:
        arancel = Arancel.objects.get(pk=pk)
        form = ArancelForm(instance=arancel)
    else:
        form = ArancelForm()
    html = render_to_string('core/partials/arancel_form_fields.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@gerente_required
def despachantes_panel(request):
    despachantes = CustomUser.objects.filter(role='despachante').order_by('username')
    form = DespachanteForm()
    return render(request, 'core/despachantes.html', {'despachantes': despachantes, 'form': form})

@gerente_required
@require_POST
def despachante_create(request):
    form = DespachanteForm(request.POST)
    if form.is_valid():
        despachante = form.save()
        html = render_to_string('core/partials/despachante_row.html', {'despachante': despachante})
        return JsonResponse({'success': True, 'html': html, 'message': 'Despachante creado correctamente.'})
    error_list = []
    for field, errors in form.errors.items():
        for error in errors:
            error_list.append(f"{form.fields.get(field).label if field in form.fields else field}: {error}")
    if form.non_field_errors():
        error_list += [str(e) for e in form.non_field_errors()]
    return JsonResponse({'success': False, 'errors': error_list})

@gerente_required
@require_POST
def despachante_delete(request, pk):
    despachante = CustomUser.objects.get(pk=pk, role='despachante')
    despachante.delete()
    return JsonResponse({'success': True})

@gerente_required
@require_GET
def despachante_form(request, pk=None):
    if pk:
        despachante = CustomUser.objects.get(pk=pk, role='despachante')
        form = DespachanteForm(instance=despachante)
    else:
        form = DespachanteForm()
    html = render_to_string('core/partials/despachante_form_fields.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@gerente_required
@require_POST
def despachante_edit(request, pk):
    despachante = CustomUser.objects.get(pk=pk, role='despachante')
    form = DespachanteForm(request.POST, instance=despachante)
    if form.is_valid():
        despachante = form.save()
        html = render_to_string('core/partials/despachante_row.html', {'despachante': despachante})
        return JsonResponse({'success': True, 'html': html, 'message': 'Despachante editado correctamente.'})
    error_list = []
    for field, errors in form.errors.items():
        for error in errors:
            error_list.append(f"{form.fields.get(field).label if field in form.fields else field}: {error}")
    if form.non_field_errors():
        error_list += [str(e) for e in form.non_field_errors()]
    return JsonResponse({'success': False, 'errors': error_list})

@gerente_required
def historial_panel(request):
    despachantes = CustomUser.objects.filter(role='despachante').order_by('username')
    usuario_id = request.GET.get('usuario')
    filtro_termino = request.GET.get('filtro_termino', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '').strip()
    fecha_hasta = request.GET.get('fecha_hasta', '').strip()
    historial = HistorialBusqueda.objects.select_related('usuario').order_by('-fecha')
    if usuario_id:
        historial = historial.filter(usuario_id=usuario_id)
    exact_count = 0
    similar_count = 0
    if filtro_termino:
        filtro_norm = normalizar_termino(filtro_termino)
        exact_count = 0
        similar_count = 0
        for h in historial:
            termino_norm = normalizar_termino(h.termino)
            if termino_norm == filtro_norm:
                exact_count += 1
            elif filtro_norm in termino_norm:
                similar_count += 1
        historial = [h for h in historial if filtro_norm in normalizar_termino(h.termino)]
    if fecha_desde and fecha_hasta:
        historial = historial.filter(fecha__date__gte=fecha_desde, fecha__date__lte=fecha_hasta)
    elif fecha_desde:
        historial = historial.filter(fecha__date=fecha_desde)
    elif fecha_hasta:
        historial = historial.filter(fecha__date=fecha_hasta)
    return render(request, 'core/historial.html', {
        'despachantes': despachantes,
        'historial': historial,
        'usuario_id': usuario_id,
        'filtro_termino': filtro_termino,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'exact_count': exact_count,
        'similar_count': similar_count,
    })

# --- AJAX para panel gerente ---
@login_required
def ajax_buscar_empleados(request):
    q = request.GET.get('q', '').strip()
    empleados = CustomUser.objects.filter(role='despachante')
    if q:
        empleados = empleados.filter(
            Q(username__icontains=q) | Q(credencial__icontains=q)
        )
    data = [{'id': e.id, 'texto': f"{e.username} ({e.credencial})"} for e in empleados[:10]]
    return JsonResponse(data, safe=False)

@login_required
def ajax_tabla_empleados(request):
    filtro_id = request.GET.get('id')
    empleados = CustomUser.objects.filter(role='despachante')
    if filtro_id:
        empleados = empleados.filter(id=filtro_id)
    html = render_to_string('core/partials/tabla_empleados.html', {'empleados': empleados})
    return JsonResponse({'html': html})

@login_required
def ajax_form_empleado(request, pk=None):
    from .forms import DespachanteForm
    if pk:
        empleado = CustomUser.objects.get(pk=pk, role='despachante')
        form = DespachanteForm(instance=empleado)
    else:
        form = DespachanteForm()
    html = render_to_string('core/partials/empleado_form_fields.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def ajax_lista_usuarios(request):
    usuarios = CustomUser.objects.filter(role='despachante')
    data = [{'id': u.id, 'texto': u.username} for u in usuarios]
    return JsonResponse(data, safe=False)

@login_required
def ajax_tabla_historial(request):
    usuario_id = request.GET.get('usuario')
    historial = HistorialBusqueda.objects.select_related('usuario').order_by('-fecha')
    if usuario_id:
        historial = historial.filter(usuario_id=usuario_id)
    html = render_to_string('core/partials/tabla_historial.html', {'historial': historial})
    return JsonResponse({'html': html})

@login_required
def ajax_buscar_aranceles(request):
    q = request.GET.get('q', '').strip()
    aranceles = Arancel.objects.all()
    if q:
        aranceles = aranceles.filter(
            Q(codigo__icontains=q) | Q(descripcion__icontains=q)
        )
    data = [{'id': a.id, 'texto': f"{a.codigo} - {a.descripcion}"} for a in aranceles[:10]]
    return JsonResponse(data, safe=False)

@login_required
def ajax_tabla_aranceles(request):
    filtro_id = request.GET.get('id')
    from .models import Seccion, Capitulo
    aranceles_qs = Arancel.objects.all().select_related('capituloaranc', 'capituloaranc__seccion')
    if filtro_id:
        aranceles_qs = aranceles_qs.filter(id=filtro_id)
    aranceles = aranceles_jerarquicos(aranceles_qs)
    secciones = Seccion.objects.all().order_by('titulo')
    capitulos = Capitulo.objects.all().order_by('titulo')
    html = render_to_string('core/partials/tabla_aranceles_jerarquica.html', {'aranceles': aranceles, 'secciones': secciones, 'capitulos': capitulos})
    return JsonResponse({'html': html})

@login_required
def ajax_form_arancel(request, pk=None):
    from .forms import ArancelForm
    if pk:
        arancel = Arancel.objects.get(pk=pk)
        form = ArancelForm(instance=arancel)
    else:
        form = ArancelForm()
    html = render_to_string('core/partials/arancel_form_fields.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def ajax_form_seccion(request):
    if request.method == 'POST':
        form = SeccionForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        html = render_to_string('core/partials/seccion_form_fields.html', {'form': form}, request=request)
        return JsonResponse({'success': False, 'html': html})
    else:
        form = SeccionForm()
        html = render_to_string('core/partials/seccion_form_fields.html', {'form': form}, request=request)
        return JsonResponse({'html': html})

@login_required
def ajax_form_capitulo(request):
    if request.method == 'POST':
        form = CapituloForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        html = render_to_string('core/partials/capitulo_form_fields.html', {'form': form}, request=request)
        return JsonResponse({'success': False, 'html': html})
    else:
        form = CapituloForm()
        html = render_to_string('core/partials/capitulo_form_fields.html', {'form': form}, request=request)
        return JsonResponse({'html': html})

@gerente_required
def gerente_panel(request):
    return render(request, 'core/gerente_panel.html')

@login_required
def sugerencias_historial(request):
    q = request.GET.get('q', '').strip()
    sugerencias = []
    if q:
        sugerencias = (HistorialBusqueda.objects
            .filter(termino__icontains=q)
            .values_list('termino', flat=True)
            .distinct()[:10])
    return JsonResponse({'sugerencias': list(sugerencias)})

def normalizar_termino(termino):
    # Elimina : y - y espacios, y pasa a minúsculas
    return re.sub(r'[:\-\s]', '', termino).lower()

def aranceles_jerarquicos(aranceles_queryset):
    """
    Devuelve una lista de aranceles ordenados jerárquicamente:
    - Padres primero (por código), luego sus hijos (por código).
    """
    padres = aranceles_queryset.filter(arancel_padre__isnull=True).order_by('codigo')
    resultado = []
    for padre in padres:
        resultado.append(padre)
        hijos = aranceles_queryset.filter(arancel_padre=padre).order_by('codigo')
        resultado.extend(hijos)
    return resultado


