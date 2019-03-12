import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import { API_URL } from '../../environments/environment';
import { CatalogItem } from './catalog-item.model';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CatalogItemApiServiceService {

  constructor(private http: HttpClient) { }
  
  getCatalogItems(): Observable<Array<CatalogItem>> {
    return this.http.get<Array<CatalogItem>>(`${API_URL}/catalog/items/JSON`);
  }
}
