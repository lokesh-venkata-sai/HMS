# Hospital Management System

Frontend Code - [HMS Front-end Angular](https://github.com/Srisai27/HMS-front-end-angular)

## Introduction
The Hospital Management System is a comprehensive platform designed to streamline and optimize healthcare operations, from patient care to administrative tasks. Built using Angular for the frontend, Django for backend functionality, and MongoDB for data storage, it includes features such as patient records management, inventory control, billing, and analytics. This system empowers healthcare providers to deliver efficient, high-quality care while improving overall organizational productivity and patient outcomes.

## Technologies Used

### Backend
- Django
- MongoDB
- RESTful Web Services

### Frontend
- Angular 
- Auth0 – Third Party Authentication Service
- Bootstrap 
- HTML 
- CSS 

## Sample UI

### Home Page
![Home Page](img_1.png)

### Patient Page
![Patient Page](img.png)

## Instructions to work on Django project in Pycharm

1. **Create a Django Project**: 
    - Use the command:
    ```bash
    django-admin startproject project_name .
    ```
    - The `.` at the end tells Django to start the project in the current directory.
  
2. **Create an App in the Django Project**:
    - Use the command:
    ```bash
    django-admin startapp app_name
    ```

3. **Run the Django App**: 
    - You can run the app in two ways:
      1. Using the command:
         ```bash
         python manage.py runserver
         ```
      2. By configuring PyCharm:
         - Go to `Run` --> `Edit Configurations` --> `Add Configuration`
         - Set the path to `project_name/manage.py`
         - Set the parameters to `runserver`

4. **Additional Configuration**:
    - Every time you create an app, add it to the `INSTALLED_APPS` variable in the `settings.py` file.
    - When building APIs in Django, you can remove the "sessions" app from the `settings.py` file if not needed.

5. **URL Configuration**:
    - To map URLs to functions so that each URL redirects to a specific target (internal app mappings), add a `urls.py` file in the app folder and configure it. Example:
      ```python
      urlpatterns = [path('hello', views.say_hello)]
      ```
      Here, `say_hello` is the method name and `views` is the file that contains the method.

    - Next, configure the URL path in the main `urls.py` (present in the project folder) for external app mappings. Example:
      ```python
      urlpatterns = [path('app_name/', include('app_name.urls'))]
      ```

6. **Connecting Django with MongoDB**:
    - Install `pymongo`:
      ```bash
      pip install pymongo
      ```
    - Create a `db_connection.py` file in the main project folder and configure the database (see `db_connection.py` for an example).

    - In the `models.py` file of your app, do the following:
      ```python
      from db_connection import db
      example_collection = db['example_collection']
      ```
    - You can now use the `example_collection` variable in your views file:
      ```python
      from .models import example_collection
      ```
    - Now you are ready to use the collection variable in your code.