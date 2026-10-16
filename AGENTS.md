# AGENTS.md — Armenia Reporta

## Descripción
Plataforma web responsive para que ciudadanos de Armenia (Quindío) registren,
consulten y hagan seguimiento a problemáticas urbanas.

## Fuente de verdad
- El plan es el de Jira (proyecto EAR) y el documento `docs/` del Sprint 0.
- No inventes funcionalidades. Lo que no esté en Jira ni en `docs/` se pregunta antes de construirlo.
- Lo marcado «propuesta» o con un código D-xx está pendiente de decisión del equipo: no lo des por hecho.
- Todo el software y los servicios deben ser gratuitos para cualquier persona.

## Stack
- Backend: Python 3.12 + Django 5 + Django REST Framework (monolito modular)
- Frontend: Angular 18 (standalone components, signals) + Angular Material 18 (SPA responsive, NO PWA)
- Base de datos: PostgreSQL 16 + PostGIS 3.4 (Neon en producción, PostGIS en Docker local)
- Almacenamiento de fotos: S3 compatible (Cloudflare R2 o Supabase Storage, por elegir)
- Correo: proveedor gratuito por definir (D-07); plan B SMTP propio
- Mapa: Leaflet + teselas de OpenStreetMap
- Autenticación: JWT con expiración y bloqueo tras intentos fallidos
- Despliegue: Angular en Vercel, Django en Render (imagen Docker con GDAL y GEOS), DB en Neon
- CI/CD: GitHub Actions

## Estructura del monorepo
- backend/   → Django + DRF
- frontend/  → Angular responsive
- docs/      → arquitectura, modelo de datos, API, UX, backlog
- .github/workflows/ → integración continua

## Módulos del backend
usuarios, reportes, apoyos, estados, mapa, estadísticas, administración y catálogos.

## Comandos
- Levantar local: docker compose up (base de datos con PostGIS, API Django, servidor de Angular)
- Backend tests: cd backend && pytest
- Frontend tests: cd frontend && npm test
- Lint backend: ruff check . && black --check .
- Lint frontend: npm run lint

## Convenciones
- Ramas: feature/EAR-XX-descripcion, fix/EAR-XX-descripcion
  Ejemplos: feature/EAR-04-registro-auth, feature/EAR-05-crear-reporte
- Commits: feat(modulo): descripcion [HU-XX]
  Ejemplos: feat(auth): registro con confirmación por correo [HU-01]
            feat(reportes): formulario con hasta 3 fotos [HU-07]
- Un PR = una tarea EAR = una rama. `main` protegida y desplegable.
- Revisión cruzada por otra persona antes de fusionar.
- No secretos en el repo; usar .env y mantener .env.example.
- Jira: proyecto EAR; los sprints son las semanas. No hay puntos ni estimaciones.

## Cómo trabajar
- Antes de escribir código, lee `docs/arquitectura.md`, `docs/modelo-datos.md`, `docs/api.md` y `docs/backlog.md`.
- Un cambio = una rama = un PR = una tarea EAR.
- Pregunta antes de tocar algo fuera del alcance de la tarea actual.
- No generes migraciones sin avisar qué campos toca y por qué.
- No mezcles backend y frontend en el mismo commit salvo que la tarea lo exija (ej. endpoint nuevo + su pantalla).
- Si una decisión está marcada como «propuesta» o D-xx, detente y pregunta antes de implementarla.
- Al terminar una tarea, deja actualizada la documentación afectada en `docs/`.

## Alcance
DENTRO (historias de Jira):
registro con confirmación por correo (HU-01), login/logout JWT (HU-02),
recuperación de contraseña (HU-03), perfil (HU-04), creación de reportes con
título/descripción (mín. 20 caracteres)/categoría/hasta 3 fotos (HU-05 a HU-07),
folio único con confirmación por correo (HU-08), selector de ubicación en mapa
(HU-09), mapa público con filtros por categoría y estado (HU-10), apoyos
(HU-11), consulta de estado con línea de tiempo (HU-12), dashboard (HU-14,
HU-15, HU-16), bandeja de moderación, cambio de estado y roles (HU-17, HU-18,
HU-19).

PROPUESTA (no está en Jira, confirmar antes de construir):
listado y detalle de reportes con filtros (HU-20); criterios de HU-18;
eliminar cuenta y suprimir datos; retirar un apoyo; CRUD de categorías;
estado «Rechazado» (D-06).

FUERA:
aplicación móvil nativa, PWA, notificaciones push, aviso de reportes parecidos
al crear, IA para clasificar reportes, integración directa con sistemas
gubernamentales, sensores IoT, modelos de predicción.

## Reglas de negocio
- Estados: Reportado → En revisión → En proceso → Solucionado.
  Solo 4 estados; cada cambio queda en historial. Avanzar un estado a la vez
  es la propuesta de HU-18. «Rechazado» es una propuesta pendiente (D-06).
- Un usuario puede apoyar un reporte una sola vez.
- Solo un funcionario o administrador cambia el estado, con justificación (EAR-9, HU-18).
- Descripción mínima de 20 caracteres.
- Fotos: hasta 3 por reporte, JPG o PNG, máximo 5 MB cada una, con compresión.
- Folio único por reporte, generado al crear (HU-08).
- Categorías oficiales (5): vías, alumbrado, residuos, espacio público, señalización.
- Zonas: comunas de Armenia con polígono (MultiPolygon, SRID 4326). Fuente de los polígonos por definir (D-05).
- El enlace de recuperación de contraseña es de un solo uso y caduca en 15 minutos.
- Datos personales conforme a la Ley 1581 de 2012; el usuario acepta el tratamiento al registrarse.

## Roles del sistema (propuesta D-04)
- ciudadano: crea reportes, apoya, consulta, ve su perfil.
- funcionario: además gestiona reportes, asigna responsable y cambia estados.
- administrador: además gestiona usuarios y roles (RBAC, HU-19).

## Criterios de terminado (propuesta; Jira no define DoD)
- Criterios de aceptación de la HU (los de Jira) cumplidos.
- Probado por alguien distinto a quien programó.
- Pruebas automáticas si toca lógica de negocio.
- Responsive en computador, tableta y móvil.
- Sin secretos en el repo.
- Documentación afectada en `docs/` actualizada.
- CI en verde, cuando el equipo configure GitHub Actions (propuesta).