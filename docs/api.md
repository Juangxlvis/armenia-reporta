# API — Armenia Reporta

Base: `/api/`. Formato: JSON. Auth: JWT (Bearer). Roles: ciudadano, funcionario y administrador (propuesta, D-04).

> Cada endpoint cita la historia de Jira que lo respalda. Los marcados **(propuesta)** no tienen historia en Jira.

## Convenciones

- Paginación: `?page=&page_size=`
- Errores: `{ "detail": "...", "code": "..." }`
- Códigos: 200, 201, 204, 400, 401, 403, 404, 409, 422, 500.
- Fotos y datos de un reporte se envían como `multipart/form-data`.

## Autenticación y cuenta

| Método | Endpoint | Rol | Descripción | Historia |
|---|---|---|---|---|
| POST | /api/auth/registro/ | público | Crear cuenta, aceptar tratamiento de datos (Ley 1581); envía correo de confirmación | HU-01 |
| POST | /api/auth/confirmar/ | público | Confirmar el correo con el token recibido | HU-01 |
| POST | /api/auth/reenviar-confirmacion/ | público | Reenviar el correo de confirmación si el token expiró o no llegó | HU-01 |
| POST | /api/auth/login/ | público | Devuelve el JWT; bloqueo tras intentos fallidos | HU-02 |
| POST | /api/auth/logout/ | autenticado | Invalida el refresh token en el servidor (blacklist). El access expira solo | HU-02 |
| POST | /api/auth/refresh/ | público | Renueva el token. **Pendiente**: falta definir cómo se renueva (ADR-006) | HU-02 |
| POST | /api/auth/recuperar/ | público | Envía enlace de un solo uso que caduca en 15 minutos | HU-03 |
| POST | /api/auth/restablecer/ | público | Fija la nueva contraseña con el token del enlace | HU-03 |
| GET/PATCH | /api/auth/perfil/ | autenticado | Ver y editar datos básicos de contacto | HU-04 |
| DELETE | /api/auth/perfil/ | autenticado | Eliminar cuenta y suprimir datos **(propuesta)** | — |

> **Pendiente ADR-006:** confirmar si el refresh token se guarda en blacklist o el cierre es solo del lado cliente. Afecta a `simplejwt` con `token_blacklist`.

## Catálogos

| Método | Endpoint | Rol | Descripción | Historia |
|---|---|---|---|---|
| GET | /api/categorias/ | público | Las 5 categorías oficiales activas | HU-06 |
| POST/PATCH | /api/categorias/{id}/ | administrador | Crear, editar o desactivar categorías **(propuesta)**; cubre el requisito de agregar categorías | — |
| GET | /api/estados/ | público | Los 4 estados | EAR-7 |
| GET | /api/zonas/ | público | Comunas de Armenia | HU-15 |

## Reportes

> **HU-05 (implementado):** `POST /api/reportes/` recibe `titulo`, `descripcion`
> (mínimo 20 caracteres), `categoria` (id de una categoría activa) y la
> ubicación como `lat` y `lng` por separado; el backend las convierte a un
> `Point` (SRID 4326). El `estado` inicial «Reportado», el `usuario` (del JWT) y
> `total_apoyos=0` se asignan en el servidor y no son editables por el cliente.
>
> **HU-07 (implementado):** `POST /api/reportes/` acepta `multipart/form-data`
> con el campo opcional `fotos` (lista de hasta 3 archivos JPG o PNG, 5 MB por
> foto). Se comprimen automáticamente (redimensión a máx. 1920 px y JPEG
> calidad 85; las PNG con transparencia se conservan en PNG). Sigue funcionando
> con JSON sin fotos. El folio y el correo de confirmación (HU-08) aún no se
> implementan.

| Método | Endpoint | Rol | Descripción | Historia |
|---|---|---|---|---|
| POST | /api/reportes/ | autenticado | Crear con título, descripción (mín. 20 caracteres), categoría, ubicación y hasta 3 fotos (JPG/PNG, 5 MB). Devuelve el folio y envía correo de confirmación | HU-05 a HU-09 |
| GET | /api/reportes/ | público | Listado paginado. Filtros: categoría, estado **(propuesta)** | HU-20 |
| GET | /api/reportes/{id}/ | público | Detalle: descripción, fotos, ubicación, estado, apoyos **(propuesta)** | HU-20 |
| GET | /api/reportes/mios/ | autenticado | Reportes del usuario con su estado actual | HU-12 |
| GET | /api/reportes/{id}/historial/ | público | Línea de tiempo: fecha de cada cambio de estado y comentarios del responsable | HU-12 |
| PATCH | /api/reportes/{id}/ | dueño | Editar el reporte **(pendiente)**: el título de HU-08 habla de editar, pero la historia solo cubre el radicado | HU-08 |

## Mapa

| Método | Endpoint | Rol | Descripción | Historia |
|---|---|---|---|---|
| GET | /api/mapa/reportes/ | público | Reportes georreferenciados. `?categoria=&estado=&bbox=`. Cada elemento trae lo necesario para el pin y la ventana de resumen | HU-10 |

## Apoyos

| Método | Endpoint | Rol | Descripción | Historia |
|---|---|---|---|---|
| POST | /api/reportes/{id}/apoyos/ | autenticado | Apoyar; una sola vez por usuario (409 si ya apoyó). Devuelve el contador actualizado | HU-11 |
| DELETE | /api/reportes/{id}/apoyos/ | autenticado | Retirar el apoyo **(propuesta)** | — |

## Administración

| Método | Endpoint | Rol | Descripción | Historia |
|---|---|---|---|---|
| GET | /api/admin/reportes/ | funcionario, administrador | Bandeja paginada y ordenable. Filtros: fecha, estado, categoría, comuna. Incluye `estado_id` | HU-17 |
| PATCH | /api/admin/reportes/{id}/estado/ | funcionario, administrador | Pasa al siguiente estado permitido; la justificación es obligatoria y queda en el historial con usuario y fecha | HU-18 |
| PATCH | /api/admin/reportes/{id}/responsable/ | funcionario, administrador | Asignar responsable | EAR-9 |
| GET | /api/admin/usuarios/ | administrador | Listar usuarios y sus roles | HU-19 |
| PATCH | /api/admin/usuarios/{id}/ | administrador | Asignar rol o permisos (control de acceso por roles) | HU-19 |

## Estadísticas

| Método | Endpoint | Rol | Descripción | Historia |
|---|---|---|---|---|
| GET | /api/estadisticas/resumen/ | público | Totales para la landing: `total_reportes`, `en_proceso` (En revisión + En proceso), `resueltos` y `ciudadanos` | - |
| GET | /api/estadisticas/por-categoria/ | autenticado | Cantidad de reportes por categoría | HU-14 |
| GET | /api/estadisticas/por-zona/ | funcionario, administrador | Densidad por comuna para el mapa de calor. `?desde=&hasta=` | HU-15 |
| GET | /api/estadisticas/tiempos/ | funcionario, administrador | Tiempo promedio de atención y resolución por categoría y comuna (de Reportado a Solucionado) | HU-16 |

## OpenAPI

Generado desde Django REST Framework. Swagger en `/api/docs/`.