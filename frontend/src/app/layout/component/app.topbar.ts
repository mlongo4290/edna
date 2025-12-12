import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { StyleClassModule } from 'primeng/styleclass';
import { ApiService } from 'src/app/services/api.service';
import { LayoutService } from '../../services/layout.service';
import { AppConfigurator } from './app.configurator';

@Component({
    selector: 'app-topbar',
    standalone: true,
    imports: [RouterModule, CommonModule, StyleClassModule, AppConfigurator, FormsModule],
    templateUrl: './app.topbar.html'
})
export class AppTopbar {
    private apiService = inject(ApiService);
    private router = inject(Router);
    public layoutService = inject(LayoutService);

    get isAuthenticated(): boolean {
        return !!localStorage.getItem('auth_token');
    }

    toggleDarkMode() {
        this.layoutService.layoutConfig.update((state) => ({ ...state, darkTheme: !state.darkTheme }));
    }

    logout() {
        this.apiService.logout();
        this.router.navigate(['/login']);
    }
}