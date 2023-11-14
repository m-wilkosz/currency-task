# Currency task
[![](https://skills.thijs.gg/icons?i=py,django,sqlite)](https://skills.thijs.gg)

### Description
Task for job recruitment. Application has two endpoints:
- GET /currency/
  - fetch a list of all currencies already present in the local application database
- GET /currency/<first_code>/<second_code>/
  - fetch last exchange rate for <first_code>/<second_code> pair
App also offers admin panel which allow to list historical rates for specific currency pairs.

### Used third-party libraries
In this project, Celery is utilized as a task queue to schedule and execute periodic data-fetching tasks, with Redis serving as the message broker to manage these asynchronous tasks efficiently.
django-environ is used for setup an usage of environment variables. django-admin-rangefilter adds a filter by date range to the admin panel.

### Setup
Create and activate virtual environment and install dependecies
```
pipenv install
pipenv shell
```
Go to currencytask directory
```
cd currencytask
```
Generate your secret key
```
python manage.py shell
>>from django.core.management.utils import get_random_secret_key
>>print(get_random_secret_key())
```
Save the key in the .env file in the directory where settings.py is
```
in .env file:
SECRET_KEY=<your_key>
```
Make migrations and migrate
```
python manage.py makemigrations
python manage.py migrate
```
Fetch inital data and load in database
```
python manage.py fetch_data
```
Create admin user
```
python manage.py createsuperuser
```
Run application server
```
python manage.py runserver
```
Finally, run the Celery worker and beat in separate terminal windows
```
celery -A your_project_name worker -l info
celery -A your_project_name beat -l info
```
