import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { BadgeModule } from 'primeng/badge';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { ToastModule } from 'primeng/toast';
import { ApiService, Device } from '../../services/api.service';

@Component({
    selector: 'app-devices',
    standalone: true,
    imports: [
        CommonModule,
        ButtonModule,
        TableModule,
        DialogModule,
        ToastModule,
        BadgeModule,
        InputIconModule,
        IconFieldModule,
        InputTextModule
    ],
    templateUrl: './devices.html',
})
export class DeviceComponent implements OnInit {
    private apiService = inject(ApiService);
    private messageService = inject(MessageService);
    private router = inject(Router);

    devices = signal<Device[]>([]);
    totalRecords = signal(0);
    loading = signal(false);
    viewBackupModal = signal(false);
    lastLogContent = signal("");
    backupDialogHeader = signal("");
    schedulerStatus = signal<{ is_running: boolean; last_run?: string; next_run?: string; cron: string }>({
        is_running: false,
        cron: ""
    });

    ngOnInit() {
        this.loadSchedulerStatus();
        this.loadDevices();
    }

    loadSchedulerStatus() {
        this.apiService.getStatus().subscribe({
            next: (status) => {
                this.schedulerStatus.set(status.scheduler);
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: error.statusText || 'Error',
                    detail: error.error?.message || 'Failed to load scheduler status'
                });
            }
        });
    }

    loadDevices() {
        this.loading.set(true);
        this.apiService.getDevices().subscribe({
            next: (response: Device[]) => {
                this.devices.set(response);
                this.totalRecords.set(response.length);
                this.loading.set(false);
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: error.statusText || 'Error',
                    detail: error.error?.message || 'Failed to load devices'
                });
                this.loading.set(false);
            }
        });
    }

    viewBackup(device: Device) {
        this.apiService.getLatestBackupContent(device.name).subscribe({
            next: (data) => {
                this.lastLogContent.set(data.content);
                this.backupDialogHeader.set(`${device.name} - Latest Backup`);
                this.viewBackupModal.set(true);
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: error.statusText || 'Error',
                    detail: error.error?.message || 'Failed to download latest backup'
                });
            }
        });
    }

    downloadBackup(device: Device) {
        this.apiService.getLatestBackupContent(device.name).subscribe({
            next: (data) => {
                const blob = new Blob([data.content], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = device.name + "_latest.cfg";
                a.click();
                window.URL.revokeObjectURL(url);
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: error.statusText || 'Error',
                    detail: error.error?.message || 'Failed to download latest backup'
                });
            }
        });
    }

    viewBackupHistory(device: Device) {
        this.router.navigate(['/backups'], { queryParams: { device: device.name } });
    }

    runBackup() {
        this.messageService.add({
            severity: 'info',
            summary: 'Backup Started',
            detail: 'Manual backup triggered'
        });

        this.apiService.triggerBackup().subscribe({
            next: () => {
                this.messageService.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: 'Backup completed successfully'
                });
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Backup failed: ' + (error.error?.message || error.message)
                });
            }
        });
    }

    stopScheduler() {
        this.apiService.stopScheduler().subscribe({
            next: () => {
                this.messageService.add({
                    severity: 'success',
                    summary: 'Scheduler Stopped',
                    detail: 'The backup scheduler has been stopped'
                });
                this.loadSchedulerStatus();
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to stop scheduler: ' + (error.error?.message || error.message)
                });
            }
        });
    }

    startScheduler() {
        this.apiService.startScheduler().subscribe({
            next: () => {
                this.messageService.add({
                    severity: 'success',
                    summary: 'Scheduler Started',
                    detail: 'The backup scheduler has been started'
                });
                this.loadSchedulerStatus();
            },
            error: (error) => {
                this.messageService.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to start scheduler: ' + (error.error?.message || error.message)
                });
            }
        });
    }
}
