import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { NgxEchartsModule } from "ngx-echarts";
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';

import { NgxJsonViewerModule } from 'ngx-json-viewer';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { NetworkScanComponent } from './network-scan/network-scan.component';
import { AnalysisComponent } from './analysis/analysis.component';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTableModule } from '@angular/material/table';
import { HomeComponent } from './home/home.component'
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSelectModule } from '@angular/material/select';
import { ConfigurationComponent } from './configuration/configuration.component';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';


@NgModule({
  declarations: [
    AppComponent,
    NetworkScanComponent,
    AnalysisComponent,
    HomeComponent,
    ConfigurationComponent
  ],
  imports: [
    BrowserModule,
    MatSidenavModule,
    MatListModule,
    MatToolbarModule,
    MatExpansionModule,
    FormsModule,
    MatSlideToggleModule,
    MatSelectModule,
    AppRoutingModule,
    MatCheckboxModule,
    MatButtonModule,
    MatTableModule,
    MatInputModule,
    MatCardModule,
    MatProgressSpinnerModule,
    NgxJsonViewerModule,
    MatIconModule,
    NgxEchartsModule.forRoot({
      echarts: () => import('echarts'), // or import('./path-to-my-custom-echarts')
    }),
    BrowserAnimationsModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule { }
