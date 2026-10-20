import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, RouterLink } from '@angular/router';
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
export class DetalleComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly reportes = inject(ReportesService);
  readonly auth = inject(AuthService);
  private readonly snackBar = inject(MatSnackBar);

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
}
