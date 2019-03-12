import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {HttpClientModule} from '@angular/common/http';

import { AppComponent } from './app.component';
import { CatalogItemComponent } from './catalog-item/catalog-item.component';
import { CatalogItemApiServiceService } from './catalog-item/catalog-item-api-service.service';
import { CategoryComponent } from './category/category.component';
import { CategoryApiService } from './category/category-api.service';

@NgModule({
  declarations: [
    AppComponent,
    CatalogItemComponent,
    CategoryComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [CatalogItemApiServiceService, CategoryApiService],
  bootstrap: [AppComponent]
})
export class AppModule { }
