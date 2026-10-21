import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

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

@Injectable({ providedIn: 'root' })
export class EstadisticasService {
  private readonly api = inject(ApiService);

  resumen(): Observable<ResumenEstadisticas> {
    return this.api.get<ResumenEstadisticas>('/estadisticas/resumen/');
  }

  porCategoria(): Observable<CategoriaConteo[]> {
    return this.api.get<CategoriaConteo[]>('/estadisticas/por-categoria/');
  }
}
