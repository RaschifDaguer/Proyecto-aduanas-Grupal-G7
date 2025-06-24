# SCAM - Sistema de Clasificación Arancelaria y Monitoreo

**Autores:** Raschif Daguer y Matthew Zambrana

---

## Descripción
SCAM es un sistema web desarrollado en Django para la gestión, consulta y monitoreo de aranceles aduaneros, con paneles diferenciados para gerente y despachante, filtros avanzados, historial de búsquedas y gestión visual de jerarquías arancelarias.

---

## Estructura del Proyecto

```
Copia-de-seguridad-main/
├── manage.py
├── requirements.txt
├── Busqueda_aduanas/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── update_codigos.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── ...
│   ├── static/
│   │   └── core/
│   │       ├── css/
│   │       │   └── custom.css
│   │       └── js/
│   │           └── gerente_panel.js
│   └── templates/
│       └── core/
│           ├── aranceles.html
│           ├── Buscadoraduanas.html
│           ├── despachantes.html
│           ├── gerente_panel.html
│           ├── historial.html
│           ├── login.html
│           └── partials/
│               ├── arancel_form_fields.html
│               ├── arancel_row.html
│               ├── capitulo_form_fields.html
│               ├── despachante_row.html
│               ├── empleado_form_fields.html
│               ├── seccion_form_fields.html
│               ├── tabla_aranceles_jerarquica.html
│               ├── tabla_aranceles.html
│               ├── tabla_empleados.html
│               └── tabla_historial.html
├── imagen/
│   └── logo-sisarm.webp
```

---

## Instalación y Puesta en Marcha

1. **Clona el repositorio y navega a la carpeta principal:**
   ```bash
   git clone <url-del-repo>
   cd Copia-de-seguridad-main
   ```

2. **Crea un entorno virtual de Python (recomendado):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   # source venv/bin/activate  # En Linux/Mac
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Realiza las migraciones de la base de datos:**
   ```bash
   python manage.py migrate
   ```

5. **Crea un superusuario para acceder al panel de administración:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecuta el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

7. **Accede a la aplicación:**
   - Panel de administración: http://127.0.0.1:8000/admin/
   - Panel principal: http://127.0.0.1:8000/

---

## Notas para desarrollo
- El sistema utiliza Django, Bootstrap 5 y jQuery.
- Los archivos estáticos y templates están organizados en la app `core`.
- Para agregar nuevas funcionalidades, crea los archivos correspondientes en la estructura indicada.
- Si agregas nuevas dependencias, recuerda actualizar `requirements.txt`.
- Si necesitas crear una nueva app, usa:
  ```bash
  python manage.py startapp nombre_app
  ```
- Para cargar datos iniciales puedes usar fixtures o el panel de administración.

---

## Recomendaciones de buenas prácticas
- Mantén el código limpio y documentado.
- Usa entornos virtuales para evitar conflictos de dependencias.
- Realiza commits frecuentes y descriptivos.
- Haz backup de la base de datos antes de cambios importantes.

---

## Licencia
Proyecto académico. Uso libre para fines educativos.
