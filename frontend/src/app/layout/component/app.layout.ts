import { CommonModule } from '@angular/common';
import { Component, inject, Renderer2, ViewChild } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { LayoutService } from '../../services/layout.service';
import { AppFooter } from './app.footer';
import { AppTopbar } from './app.topbar';

@Component({
    selector: 'app-layout',
    standalone: true,
    imports: [CommonModule, AppTopbar, RouterModule, AppFooter],
    templateUrl: './app.layout.html'
})
export class AppLayout {
    public layoutService = inject(LayoutService);
    public renderer = inject(Renderer2);
    public router = inject(Router);


    @ViewChild(AppTopbar) appTopBar!: AppTopbar;

    isOutsideClicked(event: MouseEvent) {
        const sidebarEl = document.querySelector('.layout-sidebar');
        const topbarEl = document.querySelector('.layout-menu-button');
        const eventTarget = event.target as Node;

        return !(sidebarEl?.isSameNode(eventTarget) || sidebarEl?.contains(eventTarget) || topbarEl?.isSameNode(eventTarget) || topbarEl?.contains(eventTarget));
    }
}
