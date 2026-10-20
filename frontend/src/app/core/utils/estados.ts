export interface EstadoFlujo {
  id: number;
  nombre: string;
}

export const ESTADOS_FLUJO: EstadoFlujo[] = [
  { id: 1, nombre: 'Reportado' },
  { id: 2, nombre: 'En revisión' },
  { id: 3, nombre: 'En proceso' },
  { id: 4, nombre: 'Solucionado' },
];

export function siguienteEstado(nombreActual: string): EstadoFlujo | null {
  const indice = ESTADOS_FLUJO.findIndex(
    (estado) => estado.nombre.trim().toLowerCase() === nombreActual.trim().toLowerCase(),
  );

  if (indice === -1 || indice === ESTADOS_FLUJO.length - 1) {
    return null;
  }

  return ESTADOS_FLUJO[indice + 1];
}
