import { CommonModule } from '@angular/common';
import {
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  computed,
  effect,
  inject,
  signal,
  viewChild,
} from '@angular/core';
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
import * as L from 'leaflet';
import '../../core/leaflet-global';
import 'leaflet.heat';

import {
  CategoriaConteo,
  EstadisticasService,
  FiltroFechas,
  ResumenEstadisticas,
  TiempoCategoria,
} from '../../core/services/estadisticas.service';
import { ReporteMapa, ReportesService } from '../../core/services/reportes.service';

const UBICACION_DEFECTO: [number, number] = [4.5339, -75.6811];

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
export class DashboardComponent implements OnInit, OnDestroy {
  private readonly estadisticasService = inject(EstadisticasService);
  private readonly reportesService = inject(ReportesService);

  readonly resumen = signal<ResumenEstadisticas | null>(null);
  readonly categorias = signal<CategoriaConteo[]>([]);
  readonly tiempos = signal<TiempoCategoria[]>([]);
  readonly mapaReportes = signal<ReporteMapa[]>([]);
  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);

  readonly desde = signal<Date | null>(null);
  readonly hasta = signal<Date | null>(null);

  private readonly fechas = signal<FiltroFechas>({});

  private readonly mapaCalorEl = viewChild<ElementRef<HTMLDivElement>>('mapaCalor');
  private mapaCalor: L.Map | null = null;
  private capaCalor: L.Layer | null = null;

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

  readonly puntosCalor = computed<[number, number, number][]>(() => {
    const filtro = this.fechas();
    return this.mapaReportes()
      .filter((reporte) =>
        this.dentroDeRango(reporte.creado_en, filtro.desde, filtro.hasta),
      )
      .map((reporte) => [reporte.lat, reporte.lng, 1] as [number, number, number]);
  });

  constructor() {
    effect(() => {
      const contenedor = this.mapaCalorEl();
      if (contenedor && !this.mapaCalor) {
        this.inicializarMapaCalor(contenedor.nativeElement);
      }
      this.actualizarCalor(this.puntosCalor());
    });
  }

  ngOnInit(): void {
    this.cargar();
  }

  ngOnDestroy(): void {
    if (this.mapaCalor) {
      this.mapaCalor.remove();
      this.mapaCalor = null;
    }
  }

  aplicarFechas(): void {
    this.fechas.set({
      desde: this.formatearFecha(this.desde()),
      hasta: this.formatearFecha(this.hasta()),
    });
    this.cargar();
  }

  limpiarFechas(): void {
    this.desde.set(null);
    this.hasta.set(null);
    this.fechas.set({});
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);

    const fechas = this.fechas();

    this.estadisticasService.resumen(fechas).subscribe({
      next: (datos) => this.resumen.set(datos),
      error: () => this.error.set('No se pudieron cargar las estadísticas.'),
    });

    this.estadisticasService.porCategoria(fechas).subscribe({
      next: (lista) => this.categorias.set(lista),
      error: () => this.categorias.set([]),
      complete: () => this.cargando.set(false),
    });

    this.estadisticasService.tiempos(fechas).subscribe({
      next: (lista) => this.tiempos.set(lista),
      error: () => this.tiempos.set([]),
    });

    this.reportesService.listarMapa().subscribe({
      next: (lista) => this.mapaReportes.set(lista),
      error: () => this.mapaReportes.set([]),
    });
  }

  private inicializarMapaCalor(contenedor: HTMLDivElement): void {
    this.mapaCalor = L.map(contenedor, {
      center: UBICACION_DEFECTO,
      zoom: 14,
      scrollWheelZoom: false,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(this.mapaCalor);
  }

  private actualizarCalor(puntos: [number, number, number][]): void {
    if (!this.mapaCalor) {
      return;
    }

    if (this.capaCalor) {
      this.mapaCalor.removeLayer(this.capaCalor);
      this.capaCalor = null;
    }

    if (puntos.length > 0) {
      this.capaCalor = L.heatLayer(puntos, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
      }).addTo(this.mapaCalor);
    }
  }

  private dentroDeRango(iso: string, desde?: string, hasta?: string): boolean {
    if (!desde && !hasta) {
      return true;
    }
    const fecha = iso.slice(0, 10);
    if (desde && fecha < desde) {
      return false;
    }
    if (hasta && fecha > hasta) {
      return false;
    }
    return true;
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
