import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { RouterLink } from '@angular/router';

import { AdminService, ReporteAdmin } from '../../core/services/admin.service';
import { claseEstado } from '../../core/utils/estado-chip';
import { CambiarEstadoDialogComponent } from './cambiar-estado-dialog/cambiar-estado-dialog.component';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    RouterLink,
  ],
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss'],
})
export class AdminComponent implements OnInit {
  private readonly adminService = inject(AdminService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);

  readonly columnas = ['folio', 'titulo', 'categoria', 'usuario', 'estado', 'fecha', 'acciones'];
  readonly dataSource = new MatTableDataSource<ReporteAdmin>([]);

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.adminService.listarReportes().subscribe({
      next: (lista) => {
        this.dataSource.data = lista;
        this.cargando.set(false);
      },
      error: (err: Error) => {
        this.error.set(err.message);
        this.cargando.set(false);
      },
    });
  }

  estaSolucionado(reporte: ReporteAdmin): boolean {
    return reporte.estado_nombre.trim().toLowerCase() === 'solucionado';
  }

  gestionar(reporte: ReporteAdmin): void {
    const dialogo = this.dialog.open(CambiarEstadoDialogComponent, {
      width: '480px',
      maxWidth: '95vw',
      data: reporte,
    });

    dialogo.afterClosed().subscribe((actualizado: boolean) => {
      if (actualizado) {
        this.snackBar.open('Estado actualizado correctamente', 'Cerrar', { duration: 4000 });
        this.cargar();
      }
    });
  }

  estadoClase(nombre: string): string {
    return claseEstado(nombre);
  }
}
