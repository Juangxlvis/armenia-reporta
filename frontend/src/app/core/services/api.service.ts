import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { environment } from '../../../environments/environment';

export type QueryParams = Record<
  string,
  string | number | boolean | null | undefined
>;

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  get<T>(path: string, params?: QueryParams): Observable<T> {
    return this.http
      .get<T>(this.url(path), { params: this.construirParams(params) })
      .pipe(catchError((error: unknown) => throwError(() => this.manejarError(error))));
  }

  post<T>(path: string, body: unknown): Observable<T> {
    return this.http
      .post<T>(this.url(path), body)
      .pipe(catchError((error: unknown) => throwError(() => this.manejarError(error))));
  }

  patch<T>(path: string, body: unknown): Observable<T> {
    return this.http
      .patch<T>(this.url(path), body)
      .pipe(catchError((error: unknown) => throwError(() => this.manejarError(error))));
  }

  delete<T>(path: string): Observable<T> {
    return this.http
      .delete<T>(this.url(path))
      .pipe(catchError((error: unknown) => throwError(() => this.manejarError(error))));
  }

  private url(path: string): string {
    return `${this.baseUrl}${path}`;
  }

  private construirParams(params?: QueryParams): HttpParams {
    let httpParams = new HttpParams();
    if (params) {
      for (const [clave, valor] of Object.entries(params)) {
        if (valor !== null && valor !== undefined && valor !== '') {
          httpParams = httpParams.set(clave, String(valor));
        }
      }
    }
    return httpParams;
  }

  private manejarError(error: unknown): Error {
    if (error instanceof ApiError) {
      return error;
    }
    if (error instanceof HttpErrorResponse) {
      return new ApiError(extraerMensaje(error), error.status);
    }
    if (error instanceof Error) {
      return error;
    }
    return new ApiError('Error inesperado', 0);
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

function extraerMensaje(error: HttpErrorResponse): string {
  const data: unknown = error.error;

  if (data && typeof data === 'object') {
    const objeto = data as Record<string, unknown>;

    if (typeof objeto['detail'] === 'string') {
      return objeto['detail'];
    }

    for (const clave of Object.keys(objeto)) {
      if (clave === 'detail') {
        continue;
      }
      const valor = objeto[clave];
      if (Array.isArray(valor)) {
        const primero = valor[0];
        if (typeof primero === 'string') {
          return primero;
        }
      } else if (typeof valor === 'string') {
        return valor;
      }
    }
  }

  if (error.status === 0) {
    return 'No se pudo conectar con el servidor';
  }
  return `Error del servidor (${error.status})`;
}
