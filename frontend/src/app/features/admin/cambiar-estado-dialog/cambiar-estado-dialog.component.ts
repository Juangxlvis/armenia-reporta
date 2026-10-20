import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';

import { AdminService, ReporteAdmin } from '../../../core/services/admin.service';
import { claseEstado } from '../../../core/utils/estado-chip';
import { EstadoFlujo, siguienteEstado } from '../../../core/utils/estados';

@Component({
  selector: 'app-cambiar-estado-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './cambiar-estado-dialog.component.html',
  styleUrls: ['./cambiar-estado-dialog.component.scss'],
})
export class CambiarEstadoDialogComponent {
  private readonly dialogRef = inject(MatDialogRef<CambiarEstadoDialogComponent>);
  private readonly adminService = inject(AdminService);
  private readonly snackBar = inject(MatSnackBar);

  readonly reporte = inject<ReporteAdmin>(MAT_DIALOG_DATA);
  readonly siguiente: EstadoFlujo | null = siguienteEstado(this.reporte.estado_nombre);

  readonly comentario = signal('');
  readonly guardando = signal(false);

  cancelar(): void {
    this.dialogRef.close(false);
  }

  confirmar(): void {
    const siguiente = this.siguiente;
    const comentario = this.comentario().trim();

    if (!siguiente || !comentario) {
      return;
    }

    this.guardando.set(true);
    this.adminService.cambiarEstado(this.reporte.id, siguiente.id, comentario).subscribe({
      next: () => {
        this.guardando.set(false);
        this.dialogRef.close(true);
      },
      error: (err: Error) => {
        this.guardando.set(false);
        this.snackBar.open(err.message, 'Cerrar', { duration: 5000 });
      },
    });
  }

  estadoClase(nombre: string): string {
    return claseEstado(nombre);
  }
}
