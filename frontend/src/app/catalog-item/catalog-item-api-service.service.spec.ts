import { TestBed } from '@angular/core/testing';

import { CatalogItemApiServiceService } from './catalog-item-api-service.service';

describe('CatalogItemApiServiceService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: CatalogItemApiServiceService = TestBed.get(CatalogItemApiServiceService);
    expect(service).toBeTruthy();
  });
});
