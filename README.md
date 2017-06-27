### Version 1.0
# Overview
This package is a required project of the ["Full Stack Web Developer" nanodegree][FSWD] at [Udacity]. The main objectives of this practice include building a web application, 'Catalog App', using Python-Flask library, implementing CRUD functions in the application based on a REST architecture, using OAuth to provide secure and user-specific user experience, applying skillsets such as html, css, sql, etc. There are three Python code files writen in Python 2.7.13. 
- The 'database_setupi.py' creates and configurates a database 'itemcats.db' using SQLAlchemy library; 
- The 'itempop.py' can poplulate the database with some starting data. *This is optional as the one can populate the database manually through the application.
- The 'itemcat.py' uses multiple libraries, such as Flask, SQLAlchemy, Oauth2, to setup the application server side.

# Functions
The 'Catalog App' will:
1. Display all current categories with the latest added items at '/home' page.
2. Display all the items available for certain category at the category page.
3. Display specific information an item at the item page.
4. Allow user loging. After logging in, a user can add, update, or delete item information. *Users will be able to modify only those items that they themselves have created.
5. Provide JSON endpoints at '/home/JSON'--catagories, '/catitems/<cat_name>/<int:cat_id>/items/JSON'--items in a catagory, and '/catitems/<cat_name>/<item_name>/<int:item_id>/JSON'--item info.

# How to use
The program is developed in a virtual machine of Ubuntu 16.04.2 environment. It has not been tested in other systems.
To use the program, you need to:
 - install and set up [GIT][git], [Virtual Box][vb], and [Vagrant][vag](Please open port 8000 for the application)
 - set up a command line terminal to run Python
 - install sqlalchemy, flask, and Oauth2.0
 - run the database_setupi.py in the command line
 - *(optional)run itempop.py in the command line if you want prepopulate the database
 - run item.py in the command line 
 - view the application in a browser at 'http://localhost:8000/home'

# License
MIT

***********************
  [FSWD]: <https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004>
  [Udacity]: <https://www.udacity.com>
  [git]: <https://www.virtualbox.org/wiki/Downloads>
  [vb]: <https://www.virtualbox.org/wiki/Downloads>
  [vag]: <https://www.vagrantup.com/downloads>