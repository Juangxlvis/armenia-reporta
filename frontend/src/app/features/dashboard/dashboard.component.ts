import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatNativeDateModule } from '@angular/material/core';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import {
  CategoriaConteo,
  EstadisticasService,
  FiltroFechas,
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
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
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

  readonly desde = signal<Date | null>(null);
  readonly hasta = signal<Date | null>(null);

  private readonly fechas: FiltroFechas = {};

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

  aplicarFechas(): void {
    this.fechas.desde = this.formatearFecha(this.desde());
    this.fechas.hasta = this.formatearFecha(this.hasta());
    this.cargar();
  }

  limpiarFechas(): void {
    this.desde.set(null);
    this.hasta.set(null);
    this.fechas.desde = undefined;
    this.fechas.hasta = undefined;
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);

    this.estadisticasService.resumen(this.fechas).subscribe({
      next: (datos) => this.resumen.set(datos),
      error: () => this.error.set('No se pudieron cargar las estadísticas.'),
    });

    this.estadisticasService.porCategoria(this.fechas).subscribe({
      next: (lista) => this.categorias.set(lista),
      error: () => this.categorias.set([]),
      complete: () => this.cargando.set(false),
    });
  }

  private formatearFecha(fecha: Date | null): string | undefined {
    if (!fecha) {
      return undefined;
    }
    const anio = fecha.getFullYear();
    const mes = String(fecha.getMonth() + 1).padStart(2, '0');
    const dia = String(fecha.getDate()).padStart(2, '0');
    return `${anio}-${mes}-${dia}`;
  }
}
