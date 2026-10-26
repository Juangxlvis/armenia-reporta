import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { RouterLink } from '@angular/router';
import { Subject, debounceTime, takeUntil } from 'rxjs';

import { AdminService, ReporteAdmin } from '../../core/services/admin.service';
import { CatalogosService, Categoria, Zona } from '../../core/services/catalogos.service';
import { claseEstado } from '../../core/utils/estado-chip';
import { ESTADOS_FLUJO, EstadoFlujo } from '../../core/utils/estados';
import { CambiarEstadoDialogComponent } from './cambiar-estado-dialog/cambiar-estado-dialog.component';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    RouterLink,
  ],
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss'],
})
export class AdminComponent implements OnInit, OnDestroy {
  private readonly adminService = inject(AdminService);
  private readonly catalogosService = inject(CatalogosService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  private readonly destroy$ = new Subject<void>();
  private readonly busqueda$ = new Subject<string>();

  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);

  readonly columnas = ['folio', 'titulo', 'categoria', 'zona', 'usuario', 'estado', 'fecha', 'acciones'];
  readonly dataSource = new MatTableDataSource<ReporteAdmin>([]);

  readonly categorias = signal<Categoria[]>([]);
  readonly zonas = signal<Zona[]>([]);
  readonly estados: EstadoFlujo[] = ESTADOS_FLUJO;

  readonly busqueda = signal('');
  readonly estado = signal(0);
  readonly categoria = signal(0);
  readonly zona = signal(0);

  ngOnInit(): void {
    this.busqueda$
      .pipe(debounceTime(300), takeUntil(this.destroy$))
      .subscribe(() => this.cargar());

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

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.adminService
      .listarReportes({
        search: this.busqueda().trim() || undefined,
        estado: this.estado() || undefined,
        categoria: this.categoria() || undefined,
        zona: this.zona() || undefined,
      })
      .subscribe({
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

  onBuscar(termino: string): void {
    this.busqueda.set(termino);
    this.busqueda$.next(termino);
  }

  limpiarFiltros(): void {
    this.busqueda.set('');
    this.estado.set(0);
    this.categoria.set(0);
    this.zona.set(0);
    this.cargar();
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
