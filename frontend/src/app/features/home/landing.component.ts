import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
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
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterLink } from '@angular/router';
import * as L from 'leaflet';

import {
  EstadisticasService,
  ResumenEstadisticas,
} from '../../core/services/estadisticas.service';
import { ReporteMapa, ReportesService } from '../../core/services/reportes.service';

const UBICACION_DEFECTO: [number, number] = [4.5339, -75.6811];

const COLORES_ESTADO: Record<string, string> = {
  Reportado: '#9e9e9e',
  'En revisión': '#f9a825',
  'En proceso': '#1e88e5',
  Solucionado: '#43a047',
};

interface TarjetaEstadistica {
  icono: string;
  etiqueta: string;
  valor: number;
}

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.scss'],
})
export class LandingComponent implements OnInit, AfterViewInit, OnDestroy {
  private readonly estadisticasService = inject(EstadisticasService);
  private readonly reportesService = inject(ReportesService);

  private readonly mapaEl = viewChild.required<ElementRef<HTMLDivElement>>('mapaMini');

  private mapa: L.Map | null = null;
  private readonly capaPines = L.layerGroup();

  readonly estadisticas = signal<ResumenEstadisticas | null>(null);
  readonly reportesRecientes = signal<ReporteMapa[]>([]);
  readonly cargandoMapa = signal(true);

  readonly tarjetas = computed<TarjetaEstadistica[]>(() => {
    const datos = this.estadisticas();
    if (!datos) {
      return [];
    }
    return [
      { icono: 'assignment', etiqueta: 'Reportes Registrados', valor: datos.total_reportes },
      { icono: 'pending_actions', etiqueta: 'En Proceso', valor: datos.en_proceso },
      { icono: 'check_circle', etiqueta: 'Resueltos', valor: datos.resueltos },
      { icono: 'people', etiqueta: 'Ciudadanos Participando', valor: datos.ciudadanos },
    ];
  });

  constructor() {
    effect(() => {
      this.actualizarPines(this.reportesRecientes());
    });
  }

  ngOnInit(): void {
    this.cargarEstadisticas();
    this.cargarReportesRecientes();
  }

  ngAfterViewInit(): void {
    this.inicializarMapa();
  }

  ngOnDestroy(): void {
    if (this.mapa) {
      this.mapa.remove();
      this.mapa = null;
    }
  }

  private cargarEstadisticas(): void {
    this.estadisticasService.resumen().subscribe({
      next: (datos) => this.estadisticas.set(datos),
      error: () => this.estadisticas.set(null),
    });
  }

  private cargarReportesRecientes(): void {
    this.cargandoMapa.set(true);
    this.reportesService.listarMapa().subscribe({
      next: (lista) => {
        const recientes = [...lista]
          .sort((a, b) => b.creado_en.localeCompare(a.creado_en))
          .slice(0, 10);
        this.reportesRecientes.set(recientes);
        this.cargandoMapa.set(false);
      },
      error: () => {
        this.reportesRecientes.set([]);
        this.cargandoMapa.set(false);
      },
    });
  }

  private inicializarMapa(): void {
    if (this.mapa) {
      return;
    }

    this.mapa = L.map(this.mapaEl().nativeElement, {
      center: UBICACION_DEFECTO,
      zoom: 13,
      scrollWheelZoom: false,
      dragging: false,
      doubleClickZoom: false,
      boxZoom: false,
      keyboard: false,
      touchZoom: false,
      zoomControl: false,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(this.mapa);

    this.capaPines.addTo(this.mapa);
    this.actualizarPines(this.reportesRecientes());
  }

  private actualizarPines(lista: ReporteMapa[]): void {
    if (!this.mapa) {
      return;
    }

    this.capaPines.clearLayers();

    for (const reporte of lista) {
      const marker = L.marker([reporte.lat, reporte.lng], {
        icon: this.crearIcono(this.colorEstado(reporte.estado_nombre)),
      });
      this.capaPines.addLayer(marker);
    }

    if (lista.length > 0) {
      const limites = L.latLngBounds(
        lista.map((reporte) => [reporte.lat, reporte.lng] as [number, number]),
      );
      this.mapa.fitBounds(limites, { padding: [30, 30], maxZoom: 16 });
    }
  }

  private crearIcono(color: string): L.DivIcon {
    return L.divIcon({
      className: 'pin-contenedor',
      html: `<span class="pin-estado" style="background-color:${color};"></span>`,
      iconSize: [24, 24],
      iconAnchor: [12, 24],
    });
  }

  private colorEstado(nombre: string): string {
    return COLORES_ESTADO[nombre] ?? '#9e9e9e';
  }
}
