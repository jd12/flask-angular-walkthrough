import { Component, OnInit } from '@angular/core';
import { CatalogItem } from './catalog-item.model';
import { CatalogItemApiServiceService } from './catalog-item-api-service.service'; 

@Component({
  selector: 'app-catalog-item',
  templateUrl: './catalog-item.component.html',
  styleUrls: ['./catalog-item.component.css']
})
export class CatalogItemComponent implements OnInit {

  itemList: CatalogItem[];
  constructor(private catalogItemApi: CatalogItemApiServiceService) { }

  ngOnInit() {
    this.catalogItemApi.getCatalogItems().subscribe(result => {
      this.itemList = result['items'];
      console.log(this.itemList);
    });
  }

}
