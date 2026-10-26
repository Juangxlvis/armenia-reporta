import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService, QueryParams } from './api.service';

export interface ReporteAdmin {
  id: number;
  folio: string;
  titulo: string;
  categoria_nombre: string;
  estado_nombre: string;
  usuario_nombre: string;
  zona_nombre: string | null;
  creado_en: string;
}

export interface ReporteAdminFiltros {
  search?: string;
  estado?: number;
  categoria?: number;
  zona?: number;
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  private readonly api = inject(ApiService);

  listarReportes(filtros?: ReporteAdminFiltros): Observable<ReporteAdmin[]> {
    return this.api.get<ReporteAdmin[]>('/admin/reportes/', filtros as QueryParams);
  }

  cambiarEstado(id: number, estadoId: number, comentario: string): Observable<ReporteAdmin> {
    return this.api.patch<ReporteAdmin>(`/admin/reportes/${id}/estado/`, {
      estado_id: estadoId,
      comentario,
    });
  }
}
