import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, catchError, finalize, map, of, switchMap, tap, throwError } from 'rxjs';

import { ApiService } from './api.service';

export interface Usuario {
  id: number;
  email: string;
  nombre: string;
  telefono?: string;
  rol: string;
  creado_en?: string;
}

export interface DatosRegistro {
  email: string;
  nombre: string;
  telefono?: string;
  password: string;
  acepta_datos: boolean;
}

interface RespuestaLogin {
  access: string;
  refresh: string;
}

interface Mensaje {
  detail: string;
}

const CLAVE_ACCESS = 'access_token';
const CLAVE_REFRESH = 'refresh_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(ApiService);

  private readonly _accessToken = signal<string | null>(this.leer(CLAVE_ACCESS));
  private readonly _refreshToken = signal<string | null>(this.leer(CLAVE_REFRESH));
  private readonly _usuario = signal<Usuario | null>(null);

  readonly accessToken = this._accessToken.asReadonly();
  readonly refreshToken = this._refreshToken.asReadonly();
  readonly usuario = this._usuario.asReadonly();
  readonly estaAutenticado = computed(() => this._accessToken() !== null);

  login(email: string, password: string): Observable<Usuario> {
    return this.api
      .post<RespuestaLogin>('/auth/login/', { email, password })
      .pipe(
        tap((respuesta) => this.guardarTokens(respuesta.access, respuesta.refresh)),
        switchMap(() => this.cargarPerfil()),
      );
  }

  registro(datos: DatosRegistro): Observable<Usuario> {
    return this.api.post<Usuario>('/auth/registro/', datos);
  }

  confirmar(token: string): Observable<Mensaje> {
    return this.api.post<Mensaje>('/auth/confirmar/', { token });
  }

  recuperar(email: string): Observable<Mensaje> {
    return this.api.post<Mensaje>('/auth/recuperar/', { email });
  }

  restablecer(token: string, password: string): Observable<Mensaje> {
    return this.api.post<Mensaje>('/auth/restablecer/', { token, password });
  }

  refrescarToken(): Observable<string> {
    const refresh = this._refreshToken();
    if (!refresh) {
      return throwError(() => new Error('No hay refresh token'));
    }
    return this.api.post<{ access: string }>('/auth/refresh/', { refresh }).pipe(
      tap((respuesta) => this.guardarAccess(respuesta.access)),
      map((respuesta) => respuesta.access),
    );
  }

  cargarPerfil(): Observable<Usuario> {
    return this.api.get<Usuario>('/auth/perfil/').pipe(
      tap((usuario) => this._usuario.set(usuario)),
    );
  }

  actualizarPerfil(datos: { nombre: string; telefono?: string }): Observable<Usuario> {
    return this.api.patch<Usuario>('/auth/perfil/', datos).pipe(
      tap((usuario) => this._usuario.set(usuario)),
    );
  }

  logout(): Observable<void> {
    const refresh = this._refreshToken();
    if (!refresh) {
      this.limpiarSesion();
      return of(undefined);
    }
    return this.api.post<unknown>('/auth/logout/', { refresh }).pipe(
      catchError(() => of(undefined)),
      map(() => undefined),
      finalize(() => this.limpiarSesion()),
    );
  }

  limpiarSesion(): void {
    this._accessToken.set(null);
    this._refreshToken.set(null);
    this._usuario.set(null);
    localStorage.removeItem(CLAVE_ACCESS);
    localStorage.removeItem(CLAVE_REFRESH);
  }

  private guardarTokens(access: string, refresh: string): void {
    this._accessToken.set(access);
    this._refreshToken.set(refresh);
    localStorage.setItem(CLAVE_ACCESS, access);
    localStorage.setItem(CLAVE_REFRESH, refresh);
  }

  private guardarAccess(access: string): void {
    this._accessToken.set(access);
    localStorage.setItem(CLAVE_ACCESS, access);
  }

  private leer(clave: string): string | null {
    return localStorage.getItem(clave);
  }
}
