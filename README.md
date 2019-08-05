Note: androo6 == AndrooTheChen
(androo6 is my older account with an unused email)
Worked on with 2 other contributers (not shown due to moving repo from private to public)

 Comic Exchange
================

Website URL: https://comic-exchange.herokuapp.com/ <br>
Short video demo: https://www.youtube.com/watch?v=bUpxTlfXtRc&feature=youtu.be

__app/__
Contains files for the majority of the web functionalities.

__migrations/__
Local database migration after initializing. Not used for online deployment.

__requirements.txt__
Text file containing all libaries and dependencies in development. This file is read from Heroku when depolying.

<br>

Database tables:
----------------
__app/models.py__
All tables and their schema in the database are initialized here.

User registration and login:
----------------
__app/auth/forms.py__
Class for Flask form objects to create new users when registering or logging in.

__app/auth/views.py__
Handles instantianted Flask form objects to add new users into the Users table or authenticate existing users when logging in (deals with Users table).

Comic book listings:
----------------
__app/listings/forms.py__
Class for Flask form objects to create, modifying, or editing listings.

__app/listings/ml.py__
Performs ML inference for reccomending new listings based on user's clicked listings.

__app/listings/views.py__
Handles instantianted Flask form objects to add, modify, or edit listings (deals with ComicBook, Author, Selling,and Sold tables).

<br>

ER Diagram:
----------------
![alt text](https://github.com/AndrooTheChen/Comic-Exchange/blob/master/Final_ER_Diagram.png)

<br>

References:
----------------
https://scotch.io/tutorials/build-a-crud-web-app-with-python-and-flask-part-one <br>
https://scotch.io/tutorials/build-a-crud-web-app-with-python-and-flask-part-two <br>
https://scotch.io/tutorials/build-a-crud-web-app-with-python-and-flask-part-three <br>
And LOTS of StackOverflow...




