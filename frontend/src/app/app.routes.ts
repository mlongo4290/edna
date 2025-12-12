import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { AppLayout } from './layout/component/app.layout';
import { BackupsComponent } from './pages/backups/backups';
import { DeviceComponent } from './pages/devices/devices';
import { LoginComponent } from './pages/login/login';
import { Notfound } from './pages/notfound/notfound';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: '',
    component: AppLayout,
    canActivate: [AuthGuard],
    children: [
      { path: '', component: DeviceComponent },
      { path: 'devices', component: DeviceComponent },
      { path: 'backups', component: BackupsComponent },
    ]
  },
  { path: 'notfound', component: Notfound },
  { path: '**', redirectTo: '/notfound' }
];
