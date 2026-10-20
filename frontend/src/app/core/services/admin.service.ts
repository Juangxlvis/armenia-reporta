import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface ReporteAdmin {
  id: number;
  folio: string;
  titulo: string;
  categoria_nombre: string;
  estado_nombre: string;
  usuario_nombre: string;
  creado_en: string;
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  private readonly api = inject(ApiService);

  listarReportes(): Observable<ReporteAdmin[]> {
    return this.api.get<ReporteAdmin[]>('/admin/reportes/');
  }

  cambiarEstado(id: number, estadoId: number, comentario: string): Observable<ReporteAdmin> {
    return this.api.patch<ReporteAdmin>(`/admin/reportes/${id}/estado/`, {
      estado_id: estadoId,
      comentario,
    });
  }
}
