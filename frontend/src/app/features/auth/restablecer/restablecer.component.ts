import { Component, OnInit, inject, signal } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-restablecer',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './restablecer.component.html',
  styleUrls: ['./restablecer.component.scss'],
})
export class RestablecerComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);

  readonly form = this.fb.nonNullable.group(
    {
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmarPassword: ['', [Validators.required]],
    },
    { validators: this.passwordsCoinciden },
  );

  readonly cargando = signal(false);
  private readonly token = signal<string | null>(null);
  readonly tokenInvalido = signal(false);

  private passwordsCoinciden(group: AbstractControl): ValidationErrors | null {
    const password = group.get('password')?.value;
    const confirmar = group.get('confirmarPassword')?.value;
    return password === confirmar ? null : { noCoinciden: true };
  }

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (!token) {
      this.tokenInvalido.set(true);
      return;
    }
    this.token.set(token);
  }

  enviar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const token = this.token();
    if (!token) {
      return;
    }
    const { password } = this.form.getRawValue();
    this.cargando.set(true);
    this.auth.restablecer(token, password).subscribe({
      next: () => {
        this.cargando.set(false);
        this.snackBar.open('Contraseña restablecida', 'Cerrar', { duration: 5000 });
        void this.router.navigate(['/auth/login']);
      },
      error: (error: Error) => {
        this.cargando.set(false);
        this.snackBar.open(error.message, 'Cerrar', { duration: 5000 });
      },
    });
  }
}
