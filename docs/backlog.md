# Backlog — Armenia Reporta

Fuente de verdad: Jira, proyecto EAR, al 13 de octubre de 2026. Seis tareas con 18 historias de usuario como subtareas (semanas 2 a 4) y cinco tareas sin historias (semanas 5 y 6). Todas están en estado Backlog, con prioridad Medium y **sin estimación**: este backlog no usa puntos, MoSCoW ni épicas. Los sprints son las semanas de Jira.

## Semana 1 — tareas hechas

| Clave | Tarea | Responsable | Estado |
|---|---|---|---|
| EAR-1 | Encuesta en línea, definición del problema y lluvia de ideas | Ana V | Hecho |
| EAR-2 | Wireframes de baja fidelidad y prototipo navegable | Isabella | Hecho |
| EAR-3 | Sprint 0: arquitectura, modelo de BD, backlog y entorno | Juan | Hecho (evidencia: documento «Sprint 0 – Armenia Reporta») |

## Semana 2

### EAR-4 · registro y autenticación de usuarios (Juan)
| Clave | Historia | Criterio clave |
|---|---|---|
| EAR-15 | HU-01 Registro de nuevos ciudadanos con validación de datos | Correo único, contraseña segura, cuenta confirmada, acepta la política de datos (Ley 1581) |
| EAR-17 | HU-02 Inicio y cierre de sesión seguro (JWT) | La sesión expira, control de intentos fallidos, token con expiración |
| EAR-18 | HU-03 Recuperación de contraseña por correo electrónico | Enlace de un solo uso que caduca en 15 minutos |
| EAR-20 | HU-04 Gestión y actualización de perfil de usuario | Cambios inmediatos con confirmación visual |

### EAR-5 · creación de reportes (Isabella)
| Clave | Historia | Criterio clave |
|---|---|---|
| EAR-22 | HU-05 Formulario de reporte con descripción detallada | Título y descripción de mínimo 20 caracteres con contador |
| EAR-24 | HU-06 Selección de categoría urbana estandarizada | Elegir 1 de 5 categorías oficiales |
| EAR-26 | HU-07 Carga y previsualización de evidencias fotográficas | JPG o PNG, compresión automática, máximo 3 fotos de 5 MB |
| EAR-27 | HU-08 Confirmación y edición de mis reportes | Folio único al instante, en pantalla y por correo. Aclarar: el título habla de editar, la historia no |

## Semana 3

### EAR-6 · geolocalización y mapa de consulta (Juan)
| Clave | Historia | Criterio clave |
|---|---|---|
| EAR-16 | HU-09 Selector manual de ubicación en mapa interactivo | Pin arrastrable, coordenadas automáticas |
| EAR-19 | HU-10 Mapa público de reportes | Filtros por categoría y estado, pines distintos, ventana de resumen |
| — | HU-20 Listado y detalle de reportes **(propuesta, no está en Jira)** | Listado paginado con filtros y detalle con botón Apoyar. Sin responsable |

### EAR-7 · apoyo a reportes y estados de seguimiento
| Clave | Historia | Criterio clave | Responsable |
|---|---|---|---|
| EAR-21 | HU-11 Sistema de apoyo comunitario (votos de respaldo) | Un apoyo por usuario; contador en «tiempo real» (D-09) | Sin asignar |
| EAR-23 | HU-12 Consulta del estado de un reporte | Línea de tiempo con fecha de cada cambio y comentarios | Sin asignar |

### EAR-8 · dashboard de estadísticas y gráficos (Ana V)
| Clave | Historia | Criterio clave |
|---|---|---|
| EAR-28 | HU-14 Métricas y gráficos de reportes por categoría | Barras o dona, interactivos |
| EAR-29 | HU-15 Gráfico de reportes por zona de Armenia | Mapa de calor o agrupación, filtros por fecha |
| EAR-30 | HU-16 Indicadores de tiempos de respuesta y resolución | Tiempo entre «Reportado» y «Solucionado» por categoría y comuna |

## Semana 4

### EAR-9 · módulo administrativo e inicio de pruebas integrales (Juan)
| Clave | Historia | Criterio clave |
|---|---|---|
| EAR-31 | HU-17 Bandeja de moderación y gestión integral de reportes | Tabla paginada, orden por columnas, filtros por fecha, estado, categoría y comuna |
| EAR-32 | HU-18 Cambio de estado y registro de acciones operativas | Jira no trae criterios. Propuesta: siguiente estado permitido, justificación obligatoria, historial con usuario y fecha |
| EAR-33 | HU-19 Acceso exclusivo para administradores | Panel de usuarios y control de acceso por roles (RBAC). Corregir los roles que lista |

El plan de pruebas integrales (funcionales, de seguridad y de carga) arranca aquí y no tiene historias propias.

## Semanas 5 y 6 — tareas sin historias

| Clave | Tarea | Semana | Responsable |
|---|---|---|---|
| EAR-10 | Cierre de pruebas, corrección de bugs y despliegue | 5 (2 al 8 de noviembre) | Juan |
| EAR-11 | Talleres de socialización con juntas de acción comunal | 5 | Ana V |
| EAR-35 | Pruebas de usabilidad con usuarios (al menos 5 usuarios reales) | Sin sprint; fechas de la Semana 5 | Isabella (la descripción dice que Ana organiza) |
| EAR-12 | Documentación: manual de usuario y documentación técnica | 6 | Isabella |
| EAR-13 | Ajustes finales, informe final y preparación de la sustentación | 6 (10 al 16 de noviembre) | Ana V |

## Carga por semana (historias de Jira)

| Semana | Tareas | Historias |
|---|---|---|
| 1 | EAR-1, EAR-2, EAR-3 | Hechas |
| 2 | EAR-4, EAR-5 | 8 |
| 3 | EAR-6, EAR-7, EAR-8 | 7 (más HU-20 si se crea) |
| 4 | EAR-9 | 3 |
| 5 | EAR-10, EAR-11, EAR-35 | — |
| 6 | EAR-12, EAR-13 | — |

**Riesgo R1:** la Semana 3 concentra 7 historias y la Semana 4 solo 3. **Decisión D-02:** mover EAR-8 (dashboard) a la Semana 4.

## Regla de recorte (propuesta)

Jira no tiene prioridades diferenciadas (todo es Medium) ni estimaciones. Si una semana no cabe, se mueve la tarea completa a la semana siguiente con holgura (D-02), no se recortan historias individuales.