# AGENTS.md — Armenia Reporta

## Descripción
Plataforma web responsive para que ciudadanos de Armenia (Quindío) registren,
consulten y hagan seguimiento a problemáticas urbanas.

## Stack
- Backend: Python 3.12 + Django 5 + Django REST Framework + SimpleJWT
- Frontend: Angular 18+ + Angular Material + PWA + Leaflet
- Base de datos: PostgreSQL + PostGIS (Neon)
- Almacenamiento: S3 compatible (Cloudflare R2 o Supabase Storage)
- Despliegue: Vercel (frontend) + Render (backend) + Neon (DB)
- CI/CD: GitHub Actions

## Estructura del monorepo
- backend/   → Django + DRF
- frontend/  → Angular PWA
- docs/      → arquitectura, modelo, API, UX, backlog
- .github/workflows/ → CI

## Comandos
- Levantar local: docker compose up
- Backend tests: cd backend && pytest
- Frontend tests: cd frontend && npm test
- Lint backend: ruff check . && black --check .
- Lint frontend: npm run lint

## Convenciones
- Ramas: feature/HU-XXX-descripcion, fix/...
- Commits: feat(modulo): descripcion [HU-XXX]
- PR con revisión cruzada
- No secretos en el repo; usar .env
- Jira: proyecto EAR

## Alcance
DENTRO:
registro, autenticación, reportes con foto y categoría, mapa interactivo,
apoyos, estados (Pendiente/En revisión/En proceso/Resuelto/Rechazado),
dashboard, panel administrativo, notificaciones PWA, documentación.

FUERA:
app móvil nativa, IA para clasificar, integración con sistemas
gubernamentales, sensores IoT, análisis predictivo.

## Reglas de negocio
- Un apoyo por usuario y reporte.
- Estados y transiciones:
  Pendiente → En revisión → En proceso → Resuelto
  Pendiente → Rechazado
  En revisión → Rechazado
- Solo el administrador cambia estados.
- El reporte puede sobrevivir sin usuario (anonimización Ley 1581 de 2012).
- Datos personales conforme Ley 1581 de 2012 y Decreto 1377 de 2013.

## Definition of Done
- Criterios de aceptación cumplidos.
- Probado por alguien distinto a quien programó.
- PR fusionado con CI verde.
- Pruebas automáticas si toca lógica de negocio.
- Responsive en computador, tableta y móvil.
- Sin secretos en el repo.
- Desplegado en entorno de demostración.
- Documentación afectada actualizada.