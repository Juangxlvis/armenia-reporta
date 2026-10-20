import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';

export interface Categoria {
  id: number;
  nombre: string;
}

@Injectable({ providedIn: 'root' })
export class CatalogosService {
  private readonly api = inject(ApiService);

  listarCategorias(): Observable<Categoria[]> {
    return this.api.get<Categoria[]>('/categorias/');
  }
}
