# Google Search Walkthrough Code 

This project is a sample setup for the google search. 

Basic Steps 

- Make sure Angular is updated. You can use [this](https://update.angular.io/) site to help you.
- Put flask-cors in your backend (remember to run the command `sudo pip install flask-cors` in your vagrant box)
- Put your API_URL in the environment file
- Create the component for one of the classes in your database_setup
- Set up your model for a class in your database (remember it should match the serialize method)
- Set up the service for your class
- Add the service to your app.module (don't forget to add HttpClientModule)
- Set up your component.ts and component.html 

Make sure your backend is running and grabbing the data out of the result. 