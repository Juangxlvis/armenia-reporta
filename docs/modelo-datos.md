# Modelo de datos — Armenia Reporta

Base: PostgreSQL + PostGIS (Neon). SRID 4326. Total: 9 tablas.

## Relaciones

```text
categorias 1---N reportes N---1 usuarios
estados 1---N reportes
zonas 1---N reportes
usuarios 1---N reportes (responsable_id, nulo hasta que un funcionario lo asigna)
reportes 1---N fotos_reporte
reportes 1---N apoyos N---1 usuarios
reportes 1---N historial_estados N---1 usuarios (cambiado_por)
historial_estados N---1 estados (estado_anterior y estado_nuevo)
usuarios 1---N tokens_usuario
```

## Tablas

### usuarios
| Campo | Restricción |
|---|---|
| id | PK |
| email | único, obligatorio |
| contraseña | hash |
| nombre | |
| teléfono | |
| rol | ciudadano, funcionario o administrador (propuesta, D-04) |
| activo | boolean |
| correo_confirmado | boolean (HU-01) |
| intentos_fallidos | entero (HU-02) |
| bloqueado_hasta | timestamp, nulo (HU-02) |
| acepta_datos_en | timestamp, obligatorio (Ley 1581 de 2012) |
| creado_en | timestamp |
| actualizado_en | timestamp (opcional, para auditar cambios de perfil) |

### tokens_usuario
| Campo | Restricción |
|---|---|
| id | PK |
| usuario_id | FK usuarios |
| tipo | confirmación o recuperación |
| token | hash |
| expira_en | timestamp; el de recuperación caduca en 15 minutos (HU-03) |
| usado_en | timestamp, nulo; un solo uso |

### categorias
| Campo | Restricción |
|---|---|
| id | PK |
| nombre | único |
| activa | boolean (se desactivan, no se borran) |

Son 5 categorías oficiales (HU-06).

### estados
| Campo | Restricción |
|---|---|
| id | PK |
| código | único |
| nombre | |
| orden | entero |
| es_final | boolean |

Son 4 estados.

### zonas
| Campo | Restricción |
|---|---|
| id | PK |
| nombre | |
| geometría | MultiPolygon, SRID 4326, índice GIST |

Son las comunas de Armenia (HU-15). La fuente de los polígonos está por definir (D-05).

### reportes
| Campo | Restricción |
|---|---|
| id | PK |
| folio | único; radicado generado al enviar (HU-08); formato sugerido: `AR-2026-000001` |
| usuario_id | FK usuarios (nulo si se anonimiza, propuesta) |
| categoria_id | FK, obligatoria (HU-06) |
| estado_id | FK |
| zona_id | FK |
| responsable_id | FK usuarios, nulo hasta que un funcionario lo asigna (EAR-9) |
| título | |
| descripción | mínimo 20 caracteres (HU-05) |
| ubicación | Point, SRID 4326, índice GIST |
| total_apoyos | >= 0 |
| creado_en / actualizado_en / resuelto_en | timestamp |

Índices B-tree: estado_id, categoria_id, zona_id, creado_en.

### fotos_reporte
| Campo | Restricción |
|---|---|
| id | PK |
| reporte_id | FK |
| clave_almacenamiento | clave del objeto en S3 |
| orden | entero |
| creado_en | timestamp |

Máximo 3 por reporte y 5 MB por foto, JPG o PNG (HU-07). Se eliminan con el reporte.

### apoyos
| Campo | Restricción |
|---|---|
| id | PK |
| reporte_id | FK |
| usuario_id | FK |
| creado_en | timestamp |

UNIQUE(reporte_id, usuario_id): un apoyo por usuario y reporte (HU-11). Se eliminan con el reporte.

### historial_estados
| Campo | Restricción |
|---|---|
| id | PK |
| reporte_id | FK |
| estado_anterior_id | FK |
| estado_nuevo_id | FK |
| cambiado_por | FK usuarios |
| comentario | justificación del cambio |
| cambiado_en | timestamp |

Solo inserción. Índice por (reporte_id, cambiado_en). Alimenta la línea de tiempo (HU-12) y los tiempos de HU-16.

## Reglas de integridad

- `total_apoyos` se mantiene sincronizado con `apoyos` dentro de la misma transacción.
- Propuesta (no está en Jira): si una persona pide suprimir sus datos (Ley 1581 de 2012), sus reportes se conservan con `usuario_id` nulo para no alterar las estadísticas.
- Solo un funcionario o administrador cambia el estado, con una justificación (EAR-9, HU-18).

## Datos iniciales

**Categorías (HU-06):** vías, alumbrado, residuos, espacio público y señalización.

**Estados (EAR-7):** Reportado (inicial), En revisión, En proceso y Solucionado (final).

## Máquina de estados

```text
Reportado ──▶ En revisión ──▶ En proceso ──▶ Solucionado
```

Avanza un estado a la vez. Cada cambio queda en `historial_estados`. Los tiempos de HU-16 se calculan entre Reportado y Solucionado. El estado «Rechazado» para moderación es una propuesta pendiente (D-06).