import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_URL } from '../../environments/environment';
import { Category } from './category.model';


@Injectable({
  providedIn: 'root'
})
export class CategoryApiService {

  constructor(private http: HttpClient) { }
  
  getCategories(): Observable<Array<Category>> {
    return this.http.get<Array<Category>>(`${API_URL}/catalog/JSON`);
  }
}
