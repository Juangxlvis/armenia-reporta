import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import {
  CategoriaConteo,
  EstadisticasService,
  ResumenEstadisticas,
} from '../../core/services/estadisticas.service';

interface TarjetaTotal {
  icono: string;
  etiqueta: string;
  valor: number;
}

interface FilaCategoria {
  nombre: string;
  total: number;
  porcentaje: number;
}

interface FilaEstado {
  nombre: string;
  total: number;
  porcentaje: number;
  color: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  private readonly estadisticasService = inject(EstadisticasService);

  readonly resumen = signal<ResumenEstadisticas | null>(null);
  readonly categorias = signal<CategoriaConteo[]>([]);
  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);

  readonly fechaHoy = new Date().toLocaleDateString('es-CO', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  readonly tarjetas = computed<TarjetaTotal[]>(() => {
    const datos = this.resumen();
    if (!datos) {
      return [];
    }
    return [
      { icono: 'assignment', etiqueta: 'Reportes', valor: datos.total_reportes },
      { icono: 'pending_actions', etiqueta: 'En Proceso', valor: datos.en_proceso },
      { icono: 'check_circle', etiqueta: 'Resueltos', valor: datos.resueltos },
      { icono: 'people', etiqueta: 'Ciudadanos', valor: datos.ciudadanos },
    ];
  });

  readonly totalCategorias = computed(() =>
    this.categorias().reduce((suma, categoria) => suma + categoria.total, 0),
  );

  readonly filasCategorias = computed<FilaCategoria[]>(() => {
    const total = this.totalCategorias();
    return this.categorias().map((categoria) => ({
      nombre: categoria.categoria_nombre,
      total: categoria.total,
      porcentaje: total === 0 ? 0 : Math.round((categoria.total / total) * 100),
    }));
  });

  readonly filasEstados = computed<FilaEstado[]>(() => {
    const datos = this.resumen();
    if (!datos) {
      return [];
    }
    const total = datos.total_reportes;
    const reportados = Math.max(
      0,
      total - datos.en_proceso - datos.resueltos,
    );
    const porcentaje = (valor: number) =>
      total === 0 ? 0 : Math.round((valor / total) * 100);

    return [
      {
        nombre: 'Reportados',
        total: reportados,
        porcentaje: porcentaje(reportados),
        color: 'var(--color-estado-reportado)',
      },
      {
        nombre: 'En proceso',
        total: datos.en_proceso,
        porcentaje: porcentaje(datos.en_proceso),
        color: 'var(--color-estado-en-proceso)',
      },
      {
        nombre: 'Solucionados',
        total: datos.resueltos,
        porcentaje: porcentaje(datos.resueltos),
        color: 'var(--color-estado-solucionado)',
      },
    ];
  });

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);

    this.estadisticasService.resumen().subscribe({
      next: (datos) => this.resumen.set(datos),
      error: () => this.error.set('No se pudieron cargar las estadísticas.'),
    });

    this.estadisticasService.porCategoria().subscribe({
      next: (lista) => this.categorias.set(lista),
      error: () => this.categorias.set([]),
      complete: () => this.cargando.set(false),
    });
  }
}
