Friday, July 10, 2020
====================

## Video Resources (Kilo Platoon)
* [Week 9 Videos](https://www.youtube.com/playlist?list=PLu0CiQ7bzwESms-mvdO37u2hnduY5JbXv)

# Using Django As An API
So far we've been using Django to create full stack web applications. This type of app, where both the front and back end are coupled together into a single code base can become a monolithic (i.e., huge) application. In some cases, it works, but as applications grow to hundreds of thousands of lines of code it can become a nightmare to debug and add new features.

Enter the concept of microservices and Service Oriented Architecture (SOA). This idea builds off of Single Responsibility code in that one app does one thing. In this, we create web applications that separate the front and back end. Moving forward, we'll use Django as an API to handle reading from / writing to the database and ReactJS to handle all of our front end logic (i.e., what the user sees / interacts with).

Today we're going to create a Django API that keeps track of different wines and returns JSON instead of HTML. If you remember from the Ticketmaster challenge, we got JSON back from Ticketmaster, not HTML. Using that JSON, we were then able to populate our frontend with the correct data.

## Setting Up Our API
Let's start by creating a new Django project:

```bash
$ cd ~/Desktop
$ mkdir wine_project && cd wine_project
$ python -m venv venv
$ source venv/bin/activate
$ pip install django
$ pip install psycopg2
```

If you are having issues with psycopg2, run this command instead:
```bash
$ env LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib" pip install psycopg2
```

Continuing on...
```sh
$ django-admin startproject wine_api .
$ python manage.py startapp wines
```

If you didn't include the `.` after the `startproject` command, you'll have to move the contents of `wine_api` up one level so that your structure looks like this:

![Directory Structure](https://github.com/limaplatoon/curriculum/blob/master/week-10/directory-structure.jpg)

Then let's create our Wine model:

```python
# wines/models.py
from django.db import models

class Wine(models.Model):
    wine_name = models.CharField(max_length=255)
    price = models.CharField(max_length=10)
    varietal = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.wine_name
```

Connect `wines` to `wine_api` in `settings.py` and change our database adapter to Postgres and name our database effectively in `wine_api/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wine_api',
    }
}
```

Make the migrations with `python manage.py makemigrations` and then run them with `python manage.py migrate` and ensure no errors come up. Finally, create some dummy data to work with. Your choice here - you can either enter data using the Python shell or the admin panel. Add 2-3 wines to test our API with before moving forward.

## 1. Set up Routes
First, add the following route to your `wine_api/urls.py` file.

```python
# wine_api/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wines/', include('wines.urls')),
]
```

Next, we can set up our wines routes in `wines/urls.py`.

```python
# wines/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.wine_list, name='wine_list'),
    path('new', views.new_wine, name='new_wine'),
    path('<int:wine_id>', views.wine_detail, name='wine_detail'),
    path('<int:wine_id>/edit', views.edit_wine, name='edit_wine'),
    path('<int:wine_id>/delete', views.delete_wine, name='delete_wine'),
]
```

## 2. Set up `views.py`

Now that we have all of our routes, we need to write all the controller actions in views.py:

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import WineForm
from .models import Wine
from .serializers import WineSerializer


def wine_list(request):
    wines = Wine.objects.all()
    serialized_wines = WineSerializer(wines).all_wines
    return JsonResponse(data=serialized_wines, status=200)


def wine_detail(request, wine_id):
    wine = Wine.objects.get(id=wine_id)
    serialized_wine = WineSerializer(wine).wine_detail
    return JsonResponse(data=serialized_wine, status=200)

@csrf_exempt
def new_wine(request):
    if request.method == "POST":
        form = WineForm(request.POST)
        if form.is_valid():
            wine = form.save(commit=True)
            serialized_wine = WineSerializer(wine).wine_detail
            return JsonResponse(data=serialized_wine, status=200)

@csrf_exempt
def edit_wine(request, wine_id):
    wine = Wine.objects.get(id=wine_id)
    if request.method == "POST":
        form = WineForm(request.POST, instance=wine)
        if form.is_valid():
            wine = form.save(commit=True)
            serialized_wine = WineSerializer(wine).wine_detail
            return JsonResponse(data=serialized_wine, status=200)


@csrf_exempt
def delete_wine(request, wine_id):
    if request.method == "POST":
        wine = Wine.objects.get(id=wine_id)
        wine.delete()
    return JsonResponse(data={'status': 'Successfully deleted wine.'}, status=200)
```

## 3. Serializers
Serializing is a fancy way of saying "Convert this data from one format to another." In this case, we want to convert a Django Query object into JSON. That is, we want to make a query to the Postgres database using Django ORM and then translate its output into JSON.

Create a new file `wines/serializers.py` and copy the following code.

```python
# wines/serializers.py
from builtins import object

class WineSerializer(object):
    def __init__(self, body):
        self.body = body

    @property
    def all_wines(self):
        output = {'wines': []}

        for wine in self.body:
            wine_details = {
                'wine_name': wine.wine_name,
                'price': wine.price,
                'varietal': wine.varietal,
                'description': wine.description
            }
            output['wines'].append(wine_details)

        return output

    @property
    def wine_detail(self):
        return {
            'wine_name': self.body.wine_name,
            'price': self.body.price,
            'varietal': self.body.varietal,
            'description': self.body.description
        }
```


## 4. Forms
We need to create a form to add/edit our wines.

```python
# wines/forms.py
from django import forms
from .models import Wine

class WineForm(forms.ModelForm):
    class Meta:
        model = Wine
        fields = ('wine_name', 'price', 'varietal', 'description')
```

## 5. Test it out!
**All Wines**

Run your server:
```sh
$ python manage.py runserver
```

Download [Postman](https://www.postman.com/) and hit your endpoints!


# Deploying to Heroku
Up until now we've been running all of our Django apps locally. This is great for development, but how do we deploy our apps to a server that is accessible to the rest of the internet? There are many services online designed to make this task easy for us. Amazon Web Services (AWS) is one of the most popular, but it's learning curve is pretty high. The service we will be using today, and for future projects, is called [Heroku](https://www.heroku.com/). It's built on top of AWS, but it abstracts away a lot of the complexity so that deploying apps is super simple. Plus, it will allow us to deploy our app for free!

### Getting Django Ready For Heroku
We have to add a few things to our Django app to make sure it will run properly when we deploy it. The steps that are going to follow is based off of the [official docs](https://devcenter.heroku.com/articles/django-app-configuration).

1. Create a Procfile
    - The first thing we need to create is a `Procfile` in our app's root directory (at the same level as `manage.py`). In this file, we are going to tell Heroku which web server we want to use for our app. Open the file and copy this line of code `web: gunicorn INSERT_PROJECT_NAME_HERE.wsgi`, being sure to replace "INSERT_PROJECT_NAME_HERE" with whatever the name of your app project is. In our case, it's `wine_api`.
    - Gunicorn is the server Heroku recommends we use. Install it with `pip install gunicorn`.


2. Django-Heroku
    - Most of the rest of the setup is done for us by installing a final `pip` package called `django-heroku`. Run `pip install django-heroku`.
    - Then place `import django_heroku` at the very top of your `settings.py` file and `django_heroku.settings(locals())` at the bottom of `settings.py`.

3. Requirements
    - The final thing we need to do is create our `requirements.txt` file in the root (the same level as your `venv` directory. Heroku will use this to download all our dependencies, including `gunicorn` and `django-heroku`.
      ```bash
      $ pip freeze > requirements.txt
      ```

4. Create your `.gitignore` file
    - You don't need to commit your `venv/` or any pycache's, so let's create a `.gitignore` file and add in `venv/` and `__pycache__/`.

## Creating A New Heroku App
Go to https://www.heroku.com/ and create a new free account. Once you are logged into your dashboard, click the link to create a new app. Give the app a name and click 'Create App'. Heroku has pretty straight forward instructions on how to proceed. Follow the deployment instructions on the `Deploy` tab.

Once you are done, run your migrations: `heroku run python manage.py migrate` from the root of your project. You can visit your app by pasting the unique URL Heroku provides into your browser, or by clicking 'Open App' in the upper right corner of you Heroku dashboard. You've successfully deployed your first app!

A completed copy of today's code can be found [here in this repo](https://github.com/limaplatoon/django-complete-wine-api).

## Challenges
* First, go over this tutorial yourself
* [Schools API](https://github.com/limaplatoon/school-api)