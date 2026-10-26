import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService, QueryParams } from './api.service';

export interface ResumenEstadisticas {
  total_reportes: number;
  en_proceso: number;
  resueltos: number;
  ciudadanos: number;
}

export interface CategoriaConteo {
  categoria_nombre: string;
  total: number;
}

export interface FiltroFechas {
  desde?: string;
  hasta?: string;
}

@Injectable({ providedIn: 'root' })
export class EstadisticasService {
  private readonly api = inject(ApiService);

  resumen(fechas?: FiltroFechas): Observable<ResumenEstadisticas> {
    return this.api.get<ResumenEstadisticas>('/estadisticas/resumen/', fechas as QueryParams);
  }

  porCategoria(fechas?: FiltroFechas): Observable<CategoriaConteo[]> {
    return this.api.get<CategoriaConteo[]>('/estadisticas/por-categoria/', fechas as QueryParams);
  }
}
