# Google Search Through Item Catalog

In this project, you will create a search bar for your item catalog. This will be the final step in your FullStack education. In this project you will see the separation of concerns between a frontend and a backend. This is also the final project before you create your own project. For that reason, there is less step by step and more of a general framework to follow, much as you would have in a final project. 

## Setup
You'll notice two folders: frontend and backend. The backend already contains a VagrantFile. You should just be able to drop your catalog folder inside that folder and have everything working. You then should be able to run the following commands

```bash
cd backend
vagrant up
vagrant ssh
```

You should then be able to run your project just like you did for the last project.


The frontend is already an Angular project. To get it up and working you should run the following commands **OUTSIDE OF YOUR VAGRANTBOX** (i.e. in a separate terminal window from which you ran your backend)

```bash
cd frontend
npm install
```
You should now be able to run `ng serve` and go to `localhost:4200` to see the Angular welcome page.

## Part I - Connect Frontend and Backend 
You should create components for each of your classes in your `database_setup.py` except for user. You should then display the appropriate information for each component using your JSON methods. You may find [this](https://auth0.com/blog/using-python-flask-and-angular-to-build-modern-apps-part-1/) article helpful. 

For right now I would just be able to load the data (save the POST requests for a bonus).

## Part II - Implement Login through Angular

To me it makes more sense to handle the login on the frontend and only authorize calls to the backend if a user is logged in. 

To implement login with Angular you should use [Angular X Social Login](https://github.com/abacritt/angularx-social-login)

## Part III - Implement Google Search Bar

The final part will be implementing the Google Search Bar. It will be very similar to the Spotify API Search Bar found in [this project](https://medium.com/@nacimidjakirene/angular-search-autosuggest-with-observables-6f42987f80e6)

You will also need to add bolding to the parts of the search that match what's in the search bar. I would use a [pipe](https://angular.io/guide/pipes) to accomplish this task.

## Bonus - Implement POST Request

Finish linking your frontend by implementing the ability to add, edit, and delete to your catalog from the Angular frontend. Make sure that you are authorizing users.
