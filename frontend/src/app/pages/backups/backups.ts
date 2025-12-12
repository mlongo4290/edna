import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { TableModule } from 'primeng/table';
import { ToastModule } from 'primeng/toast';
import { ApiService, Backup } from '../../services/api.service';

@Component({
    selector: 'app-backups',
    standalone: true,
    imports: [
        CommonModule,
        ButtonModule,
        TableModule,
        DialogModule,
        ToastModule
    ],
    templateUrl: './backups.html'
})
export class BackupsComponent implements OnInit {
    private apiService = inject(ApiService);
    private messageService = inject(MessageService);
    private activatedRoute = inject(ActivatedRoute);
    private router = inject(Router)

    filterDevice: string = "";
    backupHeader = signal("Backups");
    backups = signal<Backup[]>([]);
    totalRecords = signal(0);
    loading = signal(false);
    viewBackupModal = signal(false);
    backupContent = signal("");
    backupDialogHeader = signal("");

    ngOnInit() {
        // Check for device filter in query params
        this.activatedRoute.queryParams.subscribe(params => {
            this.filterDevice = params['device'] || null;
            this.backupHeader.set(this.filterDevice ? `Backups for ${this.filterDevice}` : "Backups");
            this.loadBackups();
        });
    }

    goHome() {
        this.router.navigate(['/']);
    }

    loadBackups() {
        this.loading.set(true);

        this.apiService.getDeviceBackups(this.filterDevice).subscribe({
            next: (backups: Backup[]) => {
                this.backups.set(backups);
                this.totalRecords.set(backups.length);
                this.loading.set(false);
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to load backups'
                });
                this.loading.set(false);
            }
        });
    }

    downloadBackup(id: string) {
        this.apiService.getBackupContent(this.filterDevice, id).subscribe({
            next: (data) => {
                const blob = new Blob([data.content], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = this.filterDevice + "_" + id;
                a.click();
                window.URL.revokeObjectURL(url);
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: error.statusText || 'Error',
                    detail: error.error?.message || 'Failed to download backup'
                });
            }
        });
    }

    viewBackup(id: string) {
        this.apiService.getBackupContent(this.filterDevice, id).subscribe({
            next: (data) => {
                this.backupContent.set(data.content);
                this.backupDialogHeader.set(`${this.filterDevice} - ${id}`);
                this.viewBackupModal.set(true);
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: error.statusText || 'Error',
                    detail: error.error?.message || 'Failed to download backup'
                });
            }
        });
    }
}
