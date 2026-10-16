import { Routes } from '@angular/router';

import { AdminComponent } from './features/admin/admin.component';
import { LoginComponent } from './features/auth/login/login.component';
import { PerfilComponent } from './features/auth/perfil/perfil.component';
import { RegistroComponent } from './features/auth/registro/registro.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { LandingComponent } from './features/home/landing.component';
import { MapaComponent } from './features/mapa/mapa.component';
import { NuevoComponent } from './features/reportes/nuevo/nuevo.component';

export const routes: Routes = [
  { path: '', component: LandingComponent, title: 'Armenia Reporta' },
  { path: 'mapa', component: MapaComponent, title: 'Mapa' },
  { path: 'reportes/nuevo', component: NuevoComponent, title: 'Nuevo reporte' },
  { path: 'perfil', component: PerfilComponent, title: 'Perfil' },
  { path: 'admin', component: AdminComponent, title: 'Administración' },
  { path: 'estadisticas', component: DashboardComponent, title: 'Estadísticas' },
  { path: 'auth/login', component: LoginComponent, title: 'Iniciar sesión' },
  { path: 'auth/registro', component: RegistroComponent, title: 'Registro' },
];
