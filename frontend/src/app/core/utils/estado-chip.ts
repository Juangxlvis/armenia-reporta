const CLASES_ESTADO: Record<string, string> = {
  reportado: 'estado-reportado',
  'en revisión': 'estado-en-revision',
  'en proceso': 'estado-en-proceso',
  solucionado: 'estado-solucionado',
};

export function claseEstado(nombre: string): string {
  return CLASES_ESTADO[nombre.trim().toLowerCase()] ?? 'estado-reportado';
}
