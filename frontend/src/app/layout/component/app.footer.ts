import { Component } from '@angular/core';
import { VERSION } from '../../version';

@Component({
    standalone: true,
    selector: 'app-footer',
    templateUrl: './app.footer.html'
})
export class AppFooter {
    version = VERSION;
    githubUrl = 'https://github.com/mlongo4290/edna';
}
