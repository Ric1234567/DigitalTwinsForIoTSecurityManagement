import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AnalysisComponent } from 'src/app/analysis/analysis.component';
import { NetworkScanComponent } from 'src/app/network-scan/network-scan.component';

const routes: Routes = [
  { path: '', component: NetworkScanComponent },
  { path: 'analysis', component: AnalysisComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
