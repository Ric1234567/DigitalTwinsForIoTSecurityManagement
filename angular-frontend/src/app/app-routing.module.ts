import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AnalysisComponent } from 'src/app/analysis/analysis.component';
import { NetworkScanComponent } from 'src/app/network-scan/network-scan.component';
import { ConfigurationComponent } from './configuration/configuration.component';
import { HomeComponent } from './home/home.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'network_scan', component: NetworkScanComponent },
  { path: 'config', component: ConfigurationComponent },
  { path: 'analysis', component: AnalysisComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
