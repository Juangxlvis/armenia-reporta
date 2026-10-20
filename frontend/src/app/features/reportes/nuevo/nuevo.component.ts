import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
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

import { CatalogosService, Categoria } from '../../../core/services/catalogos.service';
import { ReportesService } from '../../../core/services/reportes.service';

const UBICACION_DEFECTO = { lat: 4.5338, lng: -75.6811 };
const MAX_FOTOS = 3;
const DESCRIPCION_MAXIMA = 500;

interface FotoSeleccionada {
  archivo: File;
  url: string;
}

@Component({
  selector: 'app-nuevo-reporte',
  standalone: true,
  imports: [
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
export class NuevoComponent implements OnInit, OnDestroy {
  private readonly fb = inject(FormBuilder);
  private readonly catalogos = inject(CatalogosService);
  private readonly reportes = inject(ReportesService);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);

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
  readonly lat = signal<number | null>(null);
  readonly lng = signal<number | null>(null);
  readonly mensajeUbicacion = signal('');
  readonly folioCreado = signal<string | null>(null);

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

  ngOnDestroy(): void {
    this.limpiarFotos();
  }

  usarUbicacionActual(): void {
    if (!('geolocation' in navigator)) {
      this.usarUbicacionDefecto(
        'Tu navegador no soporta geolocalización. Se usará el centro de Armenia.',
      );
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (posicion) => {
        this.lat.set(posicion.coords.latitude);
        this.lng.set(posicion.coords.longitude);
        this.mensajeUbicacion.set('Ubicación actual guardada.');
      },
      () => {
        this.usarUbicacionDefecto(
          'Permiso de ubicación denegado. Se usará el centro de Armenia.',
        );
      },
    );
  }

  onSeleccionarFotos(event: Event): void {
    const input = event.target as HTMLInputElement;
    const archivos = Array.from(input.files ?? []);
    const disponibles = MAX_FOTOS - this.fotos().length;

    for (const archivo of archivos.slice(0, disponibles)) {
      this.fotos.update((lista) => [
        ...lista,
        { archivo, url: URL.createObjectURL(archivo) },
      ]);
    }

    if (archivos.length > disponibles) {
      this.snackBar.open(`Solo puedes adjuntar hasta ${MAX_FOTOS} fotos`, 'Cerrar', {
        duration: 4000,
      });
    }

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
    if (lat === null || lng === null) {
      this.snackBar.open('Selecciona la ubicación del reporte', 'Cerrar', { duration: 5000 });
      return;
    }

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
    this.lat.set(null);
    this.lng.set(null);
    this.mensajeUbicacion.set('');
    this.limpiarFotos();
  }

  irAlInicio(): void {
    void this.router.navigate(['/']);
  }

  private usarUbicacionDefecto(mensaje: string): void {
    this.lat.set(UBICACION_DEFECTO.lat);
    this.lng.set(UBICACION_DEFECTO.lng);
    this.mensajeUbicacion.set(mensaje);
  }

  private limpiarFotos(): void {
    for (const foto of this.fotos()) {
      URL.revokeObjectURL(foto.url);
    }
    this.fotos.set([]);
  }
}
