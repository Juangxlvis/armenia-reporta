import { Component, OnInit, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

type Estado = 'cargando' | 'exito' | 'error';

@Component({
  selector: 'app-confirmar',
  standalone: true,
  imports: [
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './confirmar.component.html',
  styleUrls: ['./confirmar.component.scss'],
})
export class ConfirmarComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly estado = signal<Estado>('cargando');
  readonly mensaje = signal('');

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (!token) {
      this.estado.set('error');
      this.mensaje.set('Enlace inválido: falta el token');
      return;
    }
    this.auth.confirmar(token).subscribe({
      next: () => {
        this.estado.set('exito');
        this.mensaje.set('Tu cuenta fue confirmada. Ya puedes iniciar sesión.');
      },
      error: (error: Error) => {
        this.estado.set('error');
        this.mensaje.set(error.message);
      },
    });
  }

  irAlLogin(): void {
    void this.router.navigate(['/auth/login']);
  }
}
