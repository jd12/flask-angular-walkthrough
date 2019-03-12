import { TestBed } from '@angular/core/testing';

import { CategoryApiService } from './category-api.service';

describe('CategoryApiService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: CategoryApiService = TestBed.get(CategoryApiService);
    expect(service).toBeTruthy();
  });
});
