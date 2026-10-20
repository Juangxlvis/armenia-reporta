import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';

import {
  ReporteResumen,
  ReportesService,
} from '../../../core/services/reportes.service';
import { claseEstado } from '../../../core/utils/estado-chip';

@Component({
  selector: 'app-mis-reportes',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './mis-reportes.component.html',
  styleUrls: ['./mis-reportes.component.scss'],
})
export class MisReportesComponent implements OnInit {
  private readonly reportesService = inject(ReportesService);
  private readonly router = inject(Router);

  readonly reportes = signal<ReporteResumen[]>([]);
  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.reportesService.listarMios().subscribe({
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

  verDetalle(id: number): void {
    void this.router.navigate(['/reportes', id]);
  }

  crearReporte(): void {
    void this.router.navigate(['/reportes/nuevo']);
  }

  fotoUrl(reporte: ReporteResumen): string | null {
    return reporte.primera_foto?.url ?? null;
  }

  estadoClase(nombre: string): string {
    return claseEstado(nombre);
  }
}
