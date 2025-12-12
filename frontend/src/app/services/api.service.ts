import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Device {
    name: string;
    host: string;
    device_type: string;
    last_backup?: string;
}

export interface Backup {
    filename: string;
    creation_time: string;
    elapsed_time: string;
}

export interface Status {
    scheduler: {
        is_running: boolean;
        last_run?: string;
        next_run?: string;
        cron: string;
    };
    config: {
        input: string;
        output: string;
        retention: number;
    };
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    username: string;
    role: string;
}

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private apiUrl = '/api';
    private http = inject(HttpClient);

    login(username: string, password: string): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, {
            username,
            password
        });
    }

    logout(): void {
        // Clear auth data from localStorage
        localStorage.removeItem('auth_token');
        localStorage.removeItem('username');
        localStorage.removeItem('role');
    }

    getStatus(): Observable<Status> {
        return this.http.get<Status>(`${this.apiUrl}/status`);
    }

    getDevices(): Observable<Device[]> {
        return this.http.get<Device[]>(`${this.apiUrl}/devices`);
    }

    getDeviceBackups(deviceName: string): Observable<Backup[]> {
        return this.http.get<Backup[]>(`${this.apiUrl}/devices/${deviceName}/backups`);
    }

    getBackupContent(deviceName: string, id: string): Observable<{ content: string }> {
        return this.http.get<{ content: string }>(`${this.apiUrl}/devices/${deviceName}/backups/${id}`);
    }

    getLatestBackupContent(deviceName: string): Observable<{ content: string }> {
        return this.http.get<{ content: string }>(`${this.apiUrl}/devices/${deviceName}/last_backup`);
    }

    triggerBackup(): Observable<any> {
        return this.http.post(`${this.apiUrl}/backup/run`, {});
    }

    startScheduler(): Observable<any> {
        return this.http.post(`${this.apiUrl}/scheduler/start`, {});
    }

    stopScheduler(): Observable<any> {
        return this.http.post(`${this.apiUrl}/scheduler/stop`, {});
    }
}
