# Armenia Reporta 🇨🇴

Plataforma web responsive diseñada para que los ciudadanos de Armenia (Quindío) registren, consulten y hagan seguimiento a problemáticas urbanas (vías, alumbrado, residuos, etc.).

## Tecnologías Utilizadas
*   **Backend:** Python, Django, Django REST Framework, PostgreSQL + PostGIS.
*   **Frontend:** Angular 18 (Standalone Components, Signals), Angular Material.
*   **Infraestructura:** Docker, Docker Compose, Cloudflare R2 (Almacenamiento S3), GitHub Actions (CI/CD).
*   **Metodologías:** Scrum (Sprints semanales), TDD (Desarrollo Guiado por Pruebas), Design Thinking.

## Características Principales
*   **Autenticación Segura:** Registro con validación, login JWT (con refresh tokens y blacklist), y recuperación de contraseña.
*   **Gestión de Reportes:** Creación de reportes con geolocalización (Leaflet), hasta 3 fotos (con compresión automática) y generación de folio único.
*   **Mapa Interactivo:** Visualización de reportes georreferenciados con filtros por categoría, estado y zona.
*   **Panel Administrativo:** Gestión de estados (Reportado → En revisión → En proceso → Solucionado) con historial de auditoría.
*   **Dashboard:** Estadísticas en tiempo real sobre el estado de los reportes.

## Cómo ejecutar el proyecto localmente
1. Clona el repositorio.
2. Crea un archivo `.env` basado en el `.env.example`.
3. Levanta el entorno con Docker:
   ```bash
   docker compose up -d --build