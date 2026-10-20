import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface ReporteCreado {
  id: number;
  folio: string;
  titulo: string;
  descripcion: string;
  categoria: number;
  estado: number;
  total_apoyos: number;
  creado_en: string;
}

export interface PrimeraFoto {
  url: string;
  clave_almacenamiento: string;
}

export interface ReporteResumen {
  id: number;
  folio: string;
  titulo: string;
  resumen: string;
  categoria_id: number;
  categoria_nombre: string;
  estado_id: number;
  estado_nombre: string;
  total_apoyos: number;
  creado_en: string;
  primera_foto: PrimeraFoto | null;
}

export interface FotoReporte {
  id: number;
  clave_almacenamiento: string;
  orden: number;
  url: string;
}

export interface ReporteMapa extends ReporteResumen {
  lat: number;
  lng: number;
}

export interface ReporteDetalle {
  id: number;
  folio: string;
  titulo: string;
  descripcion: string;
  categoria: { id: number; nombre: string };
  estado: { id: number; nombre: string };
  lat: number;
  lng: number;
  total_apoyos: number;
  creado_en: string;
  resuelto_en: string | null;
  fotos: FotoReporte[];
  usuario_nombre: string;
  apoyado_por_mi: boolean;
}

export interface HistorialEntrada {
  estado_anterior_nombre: string | null;
  estado_nuevo_nombre: string;
  comentario: string;
  cambiado_en: string;
}

export interface ResultadoApoyo {
  total_apoyos: number;
}

@Injectable({ providedIn: 'root' })
export class ReportesService {
  private readonly api = inject(ApiService);

  crear(formData: FormData): Observable<ReporteCreado> {
    return this.api.post<ReporteCreado>('/reportes/', formData);
  }

  listarMios(): Observable<ReporteResumen[]> {
    return this.api.get<ReporteResumen[]>('/reportes/mios/');
  }

  listarMapa(): Observable<ReporteMapa[]> {
    return this.api.get<ReporteMapa[]>('/mapa/reportes/');
  }

  obtener(id: number): Observable<ReporteDetalle> {
    return this.api.get<ReporteDetalle>(`/reportes/${id}/`);
  }

  historial(id: number): Observable<HistorialEntrada[]> {
    return this.api.get<HistorialEntrada[]>(`/reportes/${id}/historial/`);
  }

  apoyar(id: number): Observable<ResultadoApoyo> {
    return this.api.post<ResultadoApoyo>(`/reportes/${id}/apoyos/`, {});
  }
}
