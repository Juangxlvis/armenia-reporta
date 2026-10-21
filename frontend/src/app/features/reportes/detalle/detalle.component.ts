import { CommonModule } from '@angular/common';
import {
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  ViewChild,
  inject,
  signal,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, RouterLink } from '@angular/router';
import * as L from 'leaflet';
import { forkJoin } from 'rxjs';

import { ApiError } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';
import {
  HistorialEntrada,
  ReporteDetalle,
  ReportesService,
} from '../../../core/services/reportes.service';
import { claseEstado } from '../../../core/utils/estado-chip';

@Component({
  selector: 'app-detalle-reporte',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatCardModule,
    MatChipsModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './detalle.component.html',
  styleUrls: ['./detalle.component.scss'],
})
export class DetalleComponent implements OnInit, OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly reportes = inject(ReportesService);
  readonly auth = inject(AuthService);
  private readonly snackBar = inject(MatSnackBar);

  private mapaElement: ElementRef<HTMLDivElement> | undefined;
  private datosCargados = false;
  private mapa: L.Map | null = null;

  @ViewChild('mapaDetalle') set setMapa(element: ElementRef<HTMLDivElement> | undefined) {
    this.mapaElement = element;
    this.intentarInicializarMapa();
  }

  readonly reporte = signal<ReporteDetalle | null>(null);
  readonly historial = signal<HistorialEntrada[]>([]);
  readonly cargando = signal(true);
  readonly noEncontrado = signal(false);
  readonly error = signal<string | null>(null);
  readonly apoyando = signal(false);
  readonly fotoActiva = signal(0);

  private get id(): number {
    return Number(this.route.snapshot.paramMap.get('id'));
  }

  ngOnInit(): void {
    this.cargar();
  }

  ngOnDestroy(): void {
    if (this.mapa) {
      this.mapa.remove();
      this.mapa = null;
    }
  }

  cargar(): void {
    this.cargando.set(true);
    this.noEncontrado.set(false);
    this.error.set(null);

    forkJoin({
      reporte: this.reportes.obtener(this.id),
      historial: this.reportes.historial(this.id),
    }).subscribe({
      next: ({ reporte, historial }) => {
        this.reporte.set(reporte);
        this.historial.set(historial);
        this.cargando.set(false);
        this.datosCargados = true;
        this.intentarInicializarMapa();
        setTimeout(() => {
          if (this.mapa) {
            this.mapa.invalidateSize();
          }
        }, 200);
      },
      error: (err: Error) => {
        this.cargando.set(false);
        if (err instanceof ApiError && err.status === 404) {
          this.noEncontrado.set(true);
        } else {
          this.error.set(err.message);
        }
      },
    });
  }

  apoyar(): void {
    const reporte = this.reporte();
    if (!reporte) {
      return;
    }

    this.apoyando.set(true);
    this.reportes.apoyar(reporte.id).subscribe({
      next: (resultado) => {
        this.reporte.update((actual) =>
          actual
            ? {
                ...actual,
                total_apoyos: resultado.total_apoyos,
                apoyado_por_mi: true,
              }
            : actual,
        );
        this.apoyando.set(false);
        this.snackBar.open('¡Gracias por apoyar este reporte!', 'Cerrar', { duration: 4000 });
      },
      error: (err: Error) => {
        this.apoyando.set(false);
        this.snackBar.open(err.message, 'Cerrar', { duration: 5000 });
      },
    });
  }

  seleccionarFoto(index: number): void {
    this.fotoActiva.set(index);
  }

  puedeApoyar(): boolean {
    return this.auth.estaAutenticado() && !this.reporte()?.apoyado_por_mi;
  }

  estadoClase(nombre: string): string {
    return claseEstado(nombre);
  }

  private intentarInicializarMapa(): void {
    if (this.mapa || !this.datosCargados || !this.mapaElement) {
      return;
    }
    this.inicializarMapa(this.mapaElement.nativeElement);
  }

  private inicializarMapa(contenedor: HTMLDivElement): void {
    if (this.mapa) {
      return;
    }

    const reporte = this.reporte();
    if (!reporte || !contenedor) {
      return;
    }

    console.log('INICIALIZANDO MAPA', contenedor.offsetWidth, contenedor.offsetHeight);

    const centro: [number, number] = [reporte.lat, reporte.lng];

    this.mapa = L.map(contenedor, {
      center: centro,
      zoom: 15,
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

    L.marker(centro, { icon: this.crearIcono() }).addTo(this.mapa);
  }

  private crearIcono(): L.DivIcon {
    return L.divIcon({
      className: 'pin-contenedor',
      html: `<span class="pin-estado" style="background-color:#3f51b5;"></span>`,
      iconSize: [24, 24],
      iconAnchor: [12, 24],
    });
  }
}
