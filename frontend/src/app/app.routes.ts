import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { AdminComponent } from './features/admin/admin.component';
import { ConfirmarComponent } from './features/auth/confirmar/confirmar.component';
import { LoginComponent } from './features/auth/login/login.component';
import { PerfilComponent } from './features/auth/perfil/perfil.component';
import { RecuperarComponent } from './features/auth/recuperar/recuperar.component';
import { RegistroComponent } from './features/auth/registro/registro.component';
import { RestablecerComponent } from './features/auth/restablecer/restablecer.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { LandingComponent } from './features/home/landing.component';
import { MapaComponent } from './features/mapa/mapa.component';
import { DetalleComponent } from './features/reportes/detalle/detalle.component';
import { MisReportesComponent } from './features/reportes/mis-reportes/mis-reportes.component';
import { NuevoComponent } from './features/reportes/nuevo/nuevo.component';

export const routes: Routes = [
  { path: '', component: LandingComponent, title: 'Armenia Reporta' },
  { path: 'mapa', component: MapaComponent, title: 'Mapa' },
  {
    path: 'reportes/nuevo',
    component: NuevoComponent,
    title: 'Nuevo reporte',
    canActivate: [authGuard],
  },
  {
    path: 'reportes/mios',
    component: MisReportesComponent,
    title: 'Mis reportes',
    canActivate: [authGuard],
  },
  {
    path: 'reportes/:id',
    component: DetalleComponent,
    title: 'Detalle del reporte',
  },
  {
    path: 'perfil',
    component: PerfilComponent,
    title: 'Perfil',
    canActivate: [authGuard],
  },
  {
    path: 'admin',
    component: AdminComponent,
    title: 'Administración',
    canActivate: [authGuard],
  },
  {
    path: 'estadisticas',
    component: DashboardComponent,
    title: 'Estadísticas',
    canActivate: [authGuard],
  },
  { path: 'auth/login', component: LoginComponent, title: 'Iniciar sesión' },
  { path: 'auth/registro', component: RegistroComponent, title: 'Registro' },
  { path: 'auth/confirmar', component: ConfirmarComponent, title: 'Confirmar cuenta' },
  { path: 'auth/recuperar', component: RecuperarComponent, title: 'Recuperar contraseña' },
  { path: 'auth/restablecer', component: RestablecerComponent, title: 'Restablecer contraseña' },
];
