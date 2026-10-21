import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import * as L from 'leaflet';

import { CatalogosService, Categoria } from '../../../core/services/catalogos.service';
import { ReportesService } from '../../../core/services/reportes.service';

const UBICACION_DEFECTO: [number, number] = [4.5338, -75.6811];
const MAX_FOTOS = 3;
const MAX_BYTES_FOTO = 5 * 1024 * 1024;
const DESCRIPCION_MAXIMA = 500;

interface FotoSeleccionada {
  archivo: File;
  url: string;
}

@Component({
  selector: 'app-nuevo-reporte',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './nuevo.component.html',
  styleUrls: ['./nuevo.component.scss'],
})
export class NuevoComponent implements OnInit, AfterViewInit, OnDestroy {
  private readonly fb = inject(FormBuilder);
  private readonly catalogos = inject(CatalogosService);
  private readonly reportes = inject(ReportesService);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);

  private readonly mapaEl = viewChild.required<ElementRef<HTMLDivElement>>('mapa');
  private readonly inputFotos = viewChild.required<ElementRef<HTMLInputElement>>('inputFotos');

  private mapa: L.Map | null = null;
  private marker: L.Marker | null = null;

  readonly form = this.fb.group({
    titulo: ['', [Validators.required]],
    descripcion: [
      '',
      [Validators.required, Validators.minLength(20), Validators.maxLength(DESCRIPCION_MAXIMA)],
    ],
    categoria: [null as number | null, [Validators.required]],
  });

  readonly categorias = signal<Categoria[]>([]);
  readonly categoriasCargando = signal(false);
  readonly cargando = signal(false);
  readonly fotos = signal<FotoSeleccionada[]>([]);
  readonly lat = signal<number>(UBICACION_DEFECTO[0]);
  readonly lng = signal<number>(UBICACION_DEFECTO[1]);
  readonly mensajeUbicacion = signal('');
  readonly folioCreado = signal<string | null>(null);
  readonly arrastrando = signal(false);

  readonly descripcionMaxima = DESCRIPCION_MAXIMA;

  get descripcionLongitud(): number {
    return (this.form.controls.descripcion.value ?? '').length;
  }

  get descripcionCorta(): boolean {
    const longitud = this.descripcionLongitud;
    return longitud > 0 && longitud < 20;
  }

  ngOnInit(): void {
    this.categoriasCargando.set(true);
    this.catalogos.listarCategorias().subscribe({
      next: (categorias) => {
        this.categorias.set(categorias);
        this.categoriasCargando.set(false);
      },
      error: (error: Error) => {
        this.categoriasCargando.set(false);
        this.snackBar.open(`No se pudieron cargar las categorías: ${error.message}`, 'Cerrar', {
          duration: 6000,
        });
      },
    });
  }

  ngAfterViewInit(): void {
    this.inicializarMapa();
  }

  ngOnDestroy(): void {
    this.destruirMapa();
    this.limpiarFotos();
  }

  centrarUbicacionActual(): void {
    if (!('geolocation' in navigator)) {
      this.mensajeUbicacion.set(
        'Tu navegador no soporta geolocalización. Ajusta el pin manualmente.',
      );
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (posicion) => {
        this.establecerUbicacion(posicion.coords.latitude, posicion.coords.longitude);
        this.mensajeUbicacion.set('Ubicación actual seleccionada.');
      },
      () => {
        this.mensajeUbicacion.set(
          'Permiso de ubicación denegado. Ajusta el pin manualmente.',
        );
      },
    );
  }

  abrirSelectorFotos(): void {
    this.inputFotos().nativeElement.click();
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.arrastrando.set(true);
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.arrastrando.set(false);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.arrastrando.set(false);
    this.agregarFotos(Array.from(event.dataTransfer?.files ?? []));
  }

  onSeleccionarFotos(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.agregarFotos(Array.from(input.files ?? []));
    input.value = '';
  }

  quitarFoto(index: number): void {
    const foto = this.fotos()[index];
    if (foto) {
      URL.revokeObjectURL(foto.url);
    }
    this.fotos.update((lista) => lista.filter((_, i) => i !== index));
  }

  enviar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const lat = this.lat();
    const lng = this.lng();

    const { titulo, descripcion, categoria } = this.form.getRawValue();

    const formData = new FormData();
    formData.append('titulo', titulo ?? '');
    formData.append('descripcion', descripcion ?? '');
    formData.append('categoria', String(categoria ?? ''));
    formData.append('lat', String(lat));
    formData.append('lng', String(lng));
    for (const foto of this.fotos()) {
      formData.append('fotos', foto.archivo);
    }

    this.cargando.set(true);
    this.reportes.crear(formData).subscribe({
      next: (reporte) => {
        this.cargando.set(false);
        this.folioCreado.set(reporte.folio);
        this.limpiarFotos();
      },
      error: (error: Error) => {
        this.cargando.set(false);
        this.snackBar.open(error.message, 'Cerrar', { duration: 6000 });
      },
    });
  }

  crearOtro(): void {
    this.form.reset();
    this.folioCreado.set(null);
    this.lat.set(UBICACION_DEFECTO[0]);
    this.lng.set(UBICACION_DEFECTO[1]);
    this.mensajeUbicacion.set('');
    this.limpiarFotos();
    this.destruirMapa();
    setTimeout(() => this.inicializarMapa(), 0);
  }

  irAlInicio(): void {
    void this.router.navigate(['/']);
  }

  private agregarFotos(archivos: File[]): void {
    if (archivos.length === 0) {
      return;
    }

    const disponibles = MAX_FOTOS - this.fotos().length;
    if (disponibles <= 0) {
      this.snackBar.open(`Solo puedes adjuntar hasta ${MAX_FOTOS} fotos`, 'Cerrar', {
        duration: 4000,
      });
      return;
    }

    const esImagen = (archivo: File) => archivo.type.startsWith('image/');
    const pesoValido = (archivo: File) => archivo.size <= MAX_BYTES_FOTO;

    if (archivos.some((archivo) => !esImagen(archivo))) {
      this.snackBar.open('Solo se permiten archivos de imagen (JPG o PNG)', 'Cerrar', {
        duration: 5000,
      });
    }
    if (archivos.some((archivo) => !pesoValido(archivo))) {
      this.snackBar.open('Cada foto debe pesar como máximo 5 MB', 'Cerrar', {
        duration: 5000,
      });
    }

    const validos = archivos.filter(esImagen).filter(pesoValido);
    const aAgregar = validos.slice(0, disponibles);

    for (const archivo of aAgregar) {
      this.fotos.update((lista) => [
        ...lista,
        { archivo, url: URL.createObjectURL(archivo) },
      ]);
    }

    if (validos.length > disponibles) {
      this.snackBar.open(`Solo puedes adjuntar hasta ${MAX_FOTOS} fotos`, 'Cerrar', {
        duration: 4000,
      });
    }
  }

  private establecerUbicacion(lat: number, lng: number): void {
    this.lat.set(lat);
    this.lng.set(lng);
    this.marker?.setLatLng([lat, lng]);
    this.mapa?.setView([lat, lng], this.mapa.getZoom());
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

    this.marker = L.marker(UBICACION_DEFECTO, {
      draggable: true,
      icon: this.crearIcono(),
    }).addTo(this.mapa);

    this.marker.on('dragend', () => {
      const posicion = this.marker?.getLatLng();
      if (!posicion) {
        return;
      }
      this.lat.set(posicion.lat);
      this.lng.set(posicion.lng);
      this.mensajeUbicacion.set('Ubicación seleccionada.');
    });

    this.mapa.on('click', (evento: L.LeafletMouseEvent) => {
      this.marker?.setLatLng(evento.latlng);
      this.lat.set(evento.latlng.lat);
      this.lng.set(evento.latlng.lng);
      this.mensajeUbicacion.set('Ubicación seleccionada.');
    });
  }

  private destruirMapa(): void {
    if (this.mapa) {
      this.mapa.remove();
      this.mapa = null;
    }
    this.marker = null;
  }

  private crearIcono(): L.DivIcon {
    return L.divIcon({
      className: 'pin-contenedor',
      html: `<span class="pin-estado" style="background-color:#3f51b5;"></span>`,
      iconSize: [24, 24],
      iconAnchor: [12, 24],
    });
  }

  private limpiarFotos(): void {
    for (const foto of this.fotos()) {
      URL.revokeObjectURL(foto.url);
    }
    this.fotos.set([]);
  }
}
