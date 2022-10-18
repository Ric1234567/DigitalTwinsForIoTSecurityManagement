import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NetworkScanComponent } from './network-scan.component';

describe('NetworkScanComponent', () => {
  let component: NetworkScanComponent;
  let fixture: ComponentFixture<NetworkScanComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NetworkScanComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NetworkScanComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
