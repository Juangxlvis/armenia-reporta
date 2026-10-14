# Arquitectura — Armenia Reporta

> Fuente de verdad: Jira (proyecto EAR) y el documento «Sprint 0 – Armenia Reporta». Lo que no está en Jira va marcado como **propuesta**.

## 1. Contexto

Armenia Reporta es una plataforma web responsive para que ciudadanos de Armenia (Quindío) registren, consulten y hagan seguimiento a problemáticas urbanas. Cubre registro y acceso, reportes con descripción, categoría, hasta 3 fotos y ubicación, mapa interactivo, apoyos, estados de seguimiento, dashboard de estadísticas y panel administrativo.

## 2. Restricciones que gobiernan las decisiones

- Todo el software y los servicios usados deben ser gratuitos para cualquier persona.
- Se entrega una plataforma completa y funcional, no un MVP.
- Fuera de alcance de la primera versión: aplicación móvil nativa, inteligencia artificial para clasificar reportes, integración directa con sistemas gubernamentales, sensores IoT y modelos de predicción.
- Plazo: inicio el 21 de septiembre de 2026; las historias se construyen en las semanas 2 a 4 (12 de octubre al 1 de noviembre); la Semana 5 estabiliza y despliega; hito del 100 % de ejecución el 9 de noviembre; sustentación el 16 de noviembre. Equipo de 3 personas.
- Fuera del plan, porque no está en Jira: PWA instalable y notificaciones push.

## 3. Decisiones de arquitectura (ADR)

«Decidido» = acordado en el Sprint 0. «Propuesto» = falta validarlo con Ana e Isabella.

| ID | Decisión | Estado | Justificación | Descartado y consecuencias |
|---|---|---|---|---|
| ADR-001 | Monolito modular con API REST; módulos por dominio: usuarios, reportes, apoyos, estados, mapa, estadísticas, administración y catálogos | Decidido | Tres personas y un solo desarrollador de backend; la mantenibilidad se logra con fronteras entre módulos | Descartados microservicios con broker de eventos. Un módulo podrá extraerse después si la carga lo exige |
| ADR-002 | Backend con Python, Django y Django REST Framework | Decidido | Stack que Juan domina; ORM y migraciones aceleran | Descartados FastAPI y Node/Express |
| ADR-003 | Frontend con Angular: aplicación de una sola página, por componentes y responsive | Decidido | Stack que Juan domina; el Alcance exige computador, tableta y móvil | Descartados React y plantillas de Django. PWA y push quedan fuera del plan |
| ADR-004 | PostgreSQL con extensión PostGIS, alojado en Neon | Decidido | Los reportes son datos geográficos; PostGIS da índice espacial y consultas por zona (mapa de calor, HU-15) | Descartados MySQL y SQLite. Verificar que Neon tenga PostGIS y que suspende el cómputo por inactividad |
| ADR-005 | Mapa con Leaflet y teselas de OpenStreetMap: selector de ubicación (HU-09), mapa público (HU-10) y capa de calor (HU-15) | Propuesto | Gratuito y sin clave de API | Descartado Google Maps. Respetar la política de uso de las teselas de OSM |
| ADR-006 | Autenticación con JWT de vida corta, bloqueo tras intentos fallidos (HU-02) y control de acceso por roles (HU-19) | Decidido | Desacopla el frontend (Vercel) de la API (Render) | Descartadas las sesiones de Django por depender de cookies entre dominios. Falta definir dónde se guarda el token y cómo se renueva |
| ADR-007 | Fotos en almacenamiento compatible con S3 de capa gratuita; en la base solo se guarda la clave. Hasta 3 fotos JPG o PNG de 5 MB por reporte, con compresión automática (HU-07) | Propuesto | Los archivos no deben vivir en el disco de Render ni inflar la base | Candidatos: Cloudflare R2 y Supabase Storage (verificar límites vigentes). Descartado guardar la imagen en Postgres |
| ADR-008 | Envío de correo con un servicio gratuito: confirmar cuenta (HU-01), recuperar contraseña con enlace de 15 minutos (HU-03) y confirmar el radicado (HU-08) | Propuesto | Tres historias de Jira lo exigen | Proveedor por elegir (D-07). Verificar límites de envío. Plan B: SMTP de una cuenta propia |
| ADR-009 | Despliegue: Angular en Vercel, Django en Render y base de datos en Neon | Decidido | Capas gratuitas y despliegue desde el repositorio | Descartado por ahora Docker Compose en un VPS. Render gratuito suspende el servicio por inactividad; GeoDjango necesita GDAL y GEOS, por eso se despliega con imagen Docker |
| ADR-010 | Panel administrativo propio en Angular sobre la API (HU-17, HU-18 y HU-19) | Propuesto | HU-17 pide bandeja con filtros, tabla paginada, ordenamiento y acciones rápidas | Descartado usar solo Django Admin como panel principal; puede servir para tareas internas. Cuesta más tiempo en la Semana 4 |

## 4. Diagrama de arquitectura

```text
        [Ciudadano]     [Funcionario / Administrador]
              |                    |
              v                    v
   [Frontend Angular responsive — Vercel]
     * Cuenta y sesión
     * Reportes
     * Mapa (Leaflet + OSM)
     * Panel administrativo y dashboard
              |
              |  API REST · HTTPS · JSON · JWT
              v
   [API Django REST — Render]
     * usuarios        * estados
     * reportes        * mapa
     * apoyos          * estadísticas
     * catálogos       * administración
              |
              +--> [PostgreSQL + PostGIS — Neon]   (datos)
              +--> [Almacenamiento S3 gratuito]    (fotos)
              +--> [Servicio de correo gratuito]   (confirmación, recuperación, radicado)
```

Las teselas del mapa llegan al navegador directamente desde OpenStreetMap; el resto del tráfico pasa por la API.

## 5. Módulos del backend

1. `usuarios` — registro, confirmación de correo, login/logout con JWT, recuperación de contraseña, perfil (HU-01 a HU-04) y roles (HU-19).
2. `reportes` — creación con fotos y folio (HU-05 a HU-08), listado y detalle (HU-20, propuesta), responsable asignado.
3. `apoyos` — apoyar un reporte, una vez por usuario (HU-11).
4. `estados` — catálogo de estados, historial y línea de tiempo (HU-12); cambio de estado con justificación (HU-18).
5. `mapa` — ubicación (HU-09) y consulta georreferenciada con filtros (HU-10).
6. `estadisticas` — por categoría, por zona y tiempos de respuesta (HU-14, HU-15, HU-16).
7. `administracion` — bandeja de moderación, asignación de responsables y gestión de usuarios y roles (HU-17, HU-19).
8. `catalogos` — categorías y comunas (zonas).

## 6. Despliegue

- Frontend: Vercel, root directory `frontend/`.
- Backend: Render, imagen Docker con GDAL y GEOS (GeoDjango).
- Base de datos: Neon con PostGIS habilitado.
- Almacenamiento: Cloudflare R2 o Supabase Storage (por elegir y verificar).
- Correo: servicio gratuito por elegir (D-07).
- Flujo (propuesta): `main` protegida y desplegable; despliegue automático desde el repositorio. CI con GitHub Actions no está en Jira.