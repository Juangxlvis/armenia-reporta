import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './perfil.component.html',
  styleUrls: ['./perfil.component.scss'],
})
export class PerfilComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly snackBar = inject(MatSnackBar);

  readonly form = this.fb.nonNullable.group({
    nombre: ['', [Validators.required]],
    telefono: [''],
  });

  readonly email = signal('');
  readonly rol = signal('');
  readonly cargando = signal(true);
  readonly guardando = signal(false);

  ngOnInit(): void {
    this.cargando.set(true);
    this.auth.cargarPerfil().subscribe({
      next: (usuario) => {
        this.email.set(usuario.email);
        this.rol.set(this.nombreRol(usuario.rol));
        this.form.patchValue({ nombre: usuario.nombre, telefono: usuario.telefono ?? '' });
        this.cargando.set(false);
      },
      error: (error: Error) => {
        this.cargando.set(false);
        this.snackBar.open(error.message, 'Cerrar', { duration: 5000 });
      },
    });
  }

  guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const { nombre, telefono } = this.form.getRawValue();
    this.guardando.set(true);
    this.auth.actualizarPerfil({ nombre, telefono }).subscribe({
      next: () => {
        this.guardando.set(false);
        this.snackBar.open('Perfil actualizado correctamente', 'Cerrar', { duration: 4000 });
      },
      error: (error: Error) => {
        this.guardando.set(false);
        this.snackBar.open(error.message, 'Cerrar', { duration: 5000 });
      },
    });
  }

  private nombreRol(rol: string): string {
    switch (rol) {
      case 'funcionario':
        return 'Funcionario';
      case 'administrador':
        return 'Administrador';
      default:
        return 'Ciudadano';
    }
  }
}
