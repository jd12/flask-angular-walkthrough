import { Component, OnInit } from '@angular/core';
import { CategoryApiService } from './category-api.service';
import { Category } from './category.model';

@Component({
  selector: 'app-category',
  templateUrl: './category.component.html',
  styleUrls: ['./category.component.css']
})
export class CategoryComponent implements OnInit {
  
  categories: Array<Category>;

  constructor(private categoryApi: CategoryApiService) { }

  ngOnInit() {
    this.categoryApi.getCategories().subscribe(
      result => {
        this.categories = result['categories'];
      }
    )
  }

}
