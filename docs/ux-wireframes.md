# UX y wireframes — Armenia Reporta

Fuente: wireframes de baja fidelidad y prototipo navegable (tarea EAR-2, Semana 1, hecha).

> **Revisar contra el prototipo real de EAR-2.** Este texto se alineó con las historias de Jira; lo que Jira no respalda se marcó como **(propuesta)** o se quitó. Si el prototipo ya lo muestra, se puede conservar.

## Principios

- Interfaz sencilla, intuitiva y responsive.
- Funciona en computador, tableta y móvil.
- Mapa como pieza central.
- Acciones clave en máximo 2 clics (propuesta).
- Contraste WCAG AA (propuesta).

## Pantallas

### 1. Landing / Inicio
- Mensaje: «Reporta, consulta y haz seguimiento a los problemas de tu ciudad».
- CTA: «Crear un reporte» y «Ver el mapa».
- Mapa resumen con reportes recientes.
- Indicadores generales de reportes (propuesta; salen de las estadísticas de HU-14).
- Sección «Cómo funciona».
- Footer: política de tratamiento de datos (Ley 1581), contacto, manual de usuario (EAR-12).

### 2. Iniciar sesión / Crear cuenta / Recuperar contraseña
- Login (HU-02): correo y contraseña; mensaje por intentos fallidos y por sesión expirada.
- Registro (HU-01): nombre, correo, contraseña segura, confirmación y aceptación de la política de tratamiento de datos. Luego se pide confirmar el correo.
- Recuperación (HU-03): pedir el enlace por correo y fijar la nueva contraseña; el enlace caduca en 15 minutos.

### 3. Mapa público de reportes (HU-10)
- Barra superior: logo, Inicio, Mapa, Nuevo reporte, Estadísticas, Perfil, Mis reportes.
- Filtros: categoría y estado.
- Centro: mapa de Armenia con pines de íconos o colores distintos por estado o categoría; al hacer clic, ventana emergente con el resumen del reporte.
- Leyenda.
- Vista alterna Lista (HU-20, propuesta): listado paginado con filtros por categoría y estado.
- Botón «Nuevo reporte».

### 4. Crear un reporte (HU-05 a HU-09)
- Campos: título, descripción (mínimo 20 caracteres, contador visible), categoría (obligatoria, 1 de 5), fotos, ubicación.
- Fotos (HU-07): hasta 3, JPG o PNG, máximo 5 MB cada una, con previsualización y compresión automática.
- Ubicación (HU-09): mapa de Armenia con pin arrastrable; las coordenadas se actualizan solas. Sugerir la ubicación actual (nota de Jira).
- Botones: Cancelar, Enviar.
- Confirmación (HU-08): número de radicado (folio) en pantalla; también se envía por correo.

### 5. Detalle de reporte (HU-20, propuesta; HU-11 y HU-12)
- Título, categoría, estado, folio, fecha.
- Fotos, descripción, ubicación en el mapa.
- Contador de apoyos y botón «Apoyar» (una vez por usuario; el contador se actualiza al apoyar, D-09).
- Línea de tiempo (HU-12): Reportado, En revisión, En proceso, Solucionado, con la fecha de cada cambio y los comentarios del responsable.

### 6. Mis reportes y perfil
- Mis reportes: lista con estado actual y acceso a la línea de tiempo (HU-12).
- Perfil (HU-04): ver y editar datos de contacto; los cambios se aplican de inmediato con confirmación visual.

### 7. Panel administrativo (HU-17, HU-18, HU-19)
- Menú lateral: Reportes, Estadísticas, Usuarios y roles, Cerrar sesión.
- Bandeja (HU-17): tabla paginada y ordenable por columnas, filtros por fecha, estado, categoría y comuna, acciones rápidas.
- Detalle: asignar responsable y cambiar al siguiente estado con justificación obligatoria (HU-18).
- Usuarios y roles (HU-19): asignar roles y permisos; acceso restringido por roles.

### 8. Estadísticas (dashboard)
- Gráfico de reportes por categoría, de barras o dona, interactivo (HU-14).
- Mapa de calor por zona de Armenia con filtro por fecha (HU-15).
- Indicadores de tiempo promedio de atención y resolución por categoría y comuna (HU-16).

## Flujos

**Ciudadano — reportar:** Landing → Crear reporte → Iniciar sesión (si no la tiene) → Formulario, fotos y ubicación → Enviar → Confirmación con radicado.

**Ciudadano — consultar y apoyar:** Landing → Ver mapa → Filtrar → Abrir reporte → Apoyar.

**Ciudadano — seguimiento:** Mis reportes → Detalle → Línea de tiempo.

**Funcionario / administrador — gestionar:** Login → Panel → Bandeja → Detalle → Cambiar estado con justificación → Queda en el historial.

## Componentes reutilizables

- Tarjeta de reporte.
- Chip de categoría y de estado.
- Línea de tiempo de estados.
- Filtros (selects).
- Mapa Leaflet con pines por estado.
- Modal de confirmación.
- Formulario de reporte.

## Estados de UI

- Vacío, cargando, error, sin resultados.
- Errores de validación por campo.
- Confirmaciones al crear un reporte, apoyar, cambiar estado y editar el perfil.

## Responsive

- Móvil: navegación inferior, mapa a ancho completo, filtros en un panel desplegable.
- Tableta: filtros laterales, mapa grande.
- Escritorio: mapa con filtros y resultados en columnas; panel administrativo con menú lateral.