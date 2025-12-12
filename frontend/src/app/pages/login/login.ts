import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { ToastModule } from 'primeng/toast';
import { AppTopbar } from '../../layout/component/app.topbar';
import { ApiService } from '../../services/api.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [
        AppTopbar,
        CommonModule,
        FormsModule,
        ButtonModule,
        InputTextModule,
        CardModule,
        ToastModule,
        PasswordModule
    ],
    templateUrl: './login.html',
})
export class LoginComponent {
    private apiService = inject(ApiService);
    private router = inject(Router);
    private messageService = inject(MessageService);

    username = '';
    password = '';
    isLoading = signal(false);

    login() {
        if (!this.username || !this.password) {
            this.messageService.add({
                severity: 'warn',
                summary: 'Validation Error',
                detail: 'Username and password are required'
            });
            return;
        }

        this.isLoading.set(true);
        this.apiService.login(this.username, this.password).subscribe({
            next: (response) => {
                localStorage.setItem('auth_token', response.access_token);
                localStorage.setItem('username', response.username);
                localStorage.setItem('role', response.role);

                this.messageService.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Welcome, ${response.username}!`
                });

                this.router.navigate(['/devices']);
                this.isLoading.set(false);
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: 'Login Failed',
                    detail: error.error?.detail || 'Invalid credentials'
                });
                this.isLoading.set(false);
            }
        });
    }

    logout() {
        this.apiService.logout();
        this.router.navigate(['/login']);
        this.messageService.add({
            severity: 'info',
            summary: 'Logged Out',
            detail: 'You have been logged out successfully'
        });
    }
}
