import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';

const RUTAS_SIN_REFRESH = ['/auth/login/', '/auth/refresh/', '/auth/logout/'];

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const token = auth.accessToken();
  const conAuth = token
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(conAuth).pipe(
    catchError((error: HttpErrorResponse) => {
      const debeRefrescar =
        error.status === 401 &&
        !RUTAS_SIN_REFRESH.some((ruta) => req.url.includes(ruta)) &&
        !!auth.refreshToken();

      if (!debeRefrescar) {
        return throwError(() => error);
      }

      return auth.refrescarToken().pipe(
        switchMap(() => {
          const nuevoToken = auth.accessToken();
          const reintento = req.clone({
            setHeaders: { Authorization: `Bearer ${nuevoToken}` },
          });
          return next(reintento);
        }),
        catchError((refreshError) => {
          auth.limpiarSesion();
          void router.navigate(['/auth/login']);
          return throwError(() => refreshError);
        }),
      );
    }),
  );
};
