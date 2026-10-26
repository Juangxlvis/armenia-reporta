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
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleChange, MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { Router, RouterLink } from '@angular/router';
import * as L from 'leaflet';

import { CatalogosService, Categoria, Zona } from '../../core/services/catalogos.service';
import { ReporteMapa, ReportesService } from '../../core/services/reportes.service';
import { claseEstado } from '../../core/utils/estado-chip';

const UBICACION_DEFECTO: [number, number] = [4.5339, -75.6811];

const ESTADOS: { nombre: string; color: string }[] = [
  { nombre: 'Reportado', color: '#9e9e9e' },
  { nombre: 'En revisión', color: '#f9a825' },
  { nombre: 'En proceso', color: '#1e88e5' },
  { nombre: 'Solucionado', color: '#43a047' },
];

type Vista = 'mapa' | 'lista';

@Component({
  selector: 'app-mapa',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    MatButtonModule,
    MatButtonToggleModule,
    MatCardModule,
    MatChipsModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './mapa.component.html',
  styleUrls: ['./mapa.component.scss'],
})
export class MapaComponent implements OnInit, AfterViewInit, OnDestroy {
  private readonly reportesService = inject(ReportesService);
  private readonly catalogosService = inject(CatalogosService);
  private readonly router = inject(Router);

  private readonly mapaEl = viewChild.required<ElementRef<HTMLDivElement>>('mapa');

  private mapa: L.Map | null = null;
  private readonly capaPines = L.layerGroup();
  private primerRender = true;

  readonly reportes = signal<ReporteMapa[]>([]);
  readonly categorias = signal<Categoria[]>([]);
  readonly zonas = signal<Zona[]>([]);
  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);

  readonly busqueda = signal('');
  readonly categoriaPendiente = signal<number>(0);
  readonly estadoPendiente = signal<string>('todos');
  readonly zonaPendiente = signal<number>(0);
  readonly categoriaActiva = signal<number>(0);
  readonly estadoActiva = signal<string>('todos');
  readonly zonaActiva = signal<number>(0);
  readonly vista = signal<Vista>('mapa');

  readonly estados = ESTADOS;

  readonly reportesFiltrados = computed(() => {
    const termino = this.busqueda().trim().toLowerCase();
    const categoria = this.categoriaActiva();
    const estado = this.estadoActiva();

    return this.reportes().filter((reporte) => {
      if (categoria !== 0 && reporte.categoria_id !== categoria) {
        return false;
      }
      if (estado !== 'todos' && reporte.estado_nombre !== estado) {
        return false;
      }
      if (termino) {
        const titulo = reporte.titulo.toLowerCase();
        const resumen = (reporte.resumen ?? '').toLowerCase();
        return titulo.includes(termino) || resumen.includes(termino);
      }
      return true;
    });
  });

  constructor() {
    effect(() => {
      this.actualizarPines(this.reportesFiltrados());
    });
  }

  ngOnInit(): void {
    this.catalogosService.listarCategorias().subscribe({
      next: (categorias) => this.categorias.set(categorias),
      error: () => this.categorias.set([]),
    });

    this.catalogosService.listarZonas().subscribe({
      next: (zonas) => this.zonas.set(zonas),
      error: () => this.zonas.set([]),
    });

    this.cargar();
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

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);

    const zona = this.zonaActiva() || undefined;

    this.reportesService.listarMapa(zona ? { zona } : undefined).subscribe({
      next: (lista) => {
        this.reportes.set(lista);
        this.cargando.set(false);
      },
      error: (err: Error) => {
        this.error.set(err.message);
        this.cargando.set(false);
      },
    });
  }

  aplicarFiltros(): void {
    this.categoriaActiva.set(this.categoriaPendiente());
    this.estadoActiva.set(this.estadoPendiente());
    this.zonaActiva.set(this.zonaPendiente());
    this.cargar();
  }

  limpiarFiltros(): void {
    this.busqueda.set('');
    this.categoriaPendiente.set(0);
    this.estadoPendiente.set('todos');
    this.zonaPendiente.set(0);
    this.categoriaActiva.set(0);
    this.estadoActiva.set('todos');
    this.zonaActiva.set(0);
    this.cargar();
  }

  cambiarVista(evento: MatButtonToggleChange): void {
    this.vista.set(evento.value as Vista);
    if (evento.value === 'mapa') {
      setTimeout(() => this.mapa?.invalidateSize(), 0);
    }
  }

  verDetalle(id: number): void {
    this.mapa?.closePopup();
    void this.router.navigate(['/reportes', id]);
  }

  estadoClase(nombre: string): string {
    return claseEstado(nombre);
  }

  fotoUrl(reporte: ReporteMapa): string | null {
    return reporte.primera_foto?.url ?? null;
  }

  colorEstado(nombre: string): string {
    return ESTADOS.find((estado) => estado.nombre === nombre)?.color ?? '#9e9e9e';
  }

  private inicializarMapa(): void {
    if (this.mapa) {
      return;
    }

    this.mapa = L.map(this.mapaEl().nativeElement, {
      center: UBICACION_DEFECTO,
      zoom: 14,
      scrollWheelZoom: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(this.mapa);

    this.capaPines.addTo(this.mapa);
    this.actualizarPines(this.reportesFiltrados());
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

      marker.bindPopup(this.popupHtml(reporte));
      marker.on('popupopen', () => {
        const contenedor = marker.getPopup()?.getElement();
        const boton = contenedor?.querySelector<HTMLButtonElement>('.popup-detalle');
        boton?.addEventListener('click', () => this.verDetalle(reporte.id));
      });

      this.capaPines.addLayer(marker);
    }

    if (this.primerRender && lista.length > 0) {
      this.primerRender = false;
      const limites = L.latLngBounds(
        lista.map((reporte) => [reporte.lat, reporte.lng] as [number, number]),
      );
      this.mapa.fitBounds(limites, { padding: [40, 40], maxZoom: 16 });
    }
  }

  private crearIcono(color: string): L.DivIcon {
    return L.divIcon({
      className: 'pin-contenedor',
      html: `<span class="pin-estado" style="background-color:${color};"></span>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
      popupAnchor: [0, -14],
    });
  }

  private popupHtml(reporte: ReporteMapa): string {
    return `
      <div class="popup-reporte">
        <h3>${this.escapeHtml(reporte.titulo)}</h3>
        <p class="popup-meta">${this.escapeHtml(reporte.categoria_nombre)} · ${this.escapeHtml(
          reporte.estado_nombre,
        )}</p>
        <button type="button" class="popup-detalle">Ver detalle</button>
      </div>
    `;
  }

  private escapeHtml(texto: string): string {
    return texto
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
}
