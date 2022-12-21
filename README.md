## jenfi-mail-service  

<i>Problem</i>: https://github.com/jenfi-eng/exam-long-mail-service  


### Overview  
The solution requires knowledge in data science, specifically Linear Programming; so python was an easy choice for the programming language. The use of Django framework was a strategic choice to showcase my backend skills since I am really not a data engineer. And PostgresSQL was just for fun as I have been using non-relational databases in the recent years.:)  Lastly, the use of Pulp will be discussed when we dive into the optimization problem below.
### 
Language: Python3.9.x  
Framework: Django (latest)  
Database: PostgreSQL  
Optimization Solver: Pulp

### Assumptions  
1. Parcels are queued in FIFO method but subject to the volume and capacity constraints.
2. Parcel costing is purely based on weight and will disregard the volume. 
3. Actual scheduling (with future departure dates) are not in the scope of my solution. That is, the output of the optimization solver will simply be an ordered list of trains to fill and their corresponding line to achieve the minimum cost.

### The Django app

This was mainly written using TDD (Test Driven Development). I suggest starting your review by checking out the tests first as I actually wrote them before the actual implementation.  
<b><i>tests:</i></b> https://github.com/jjacarillo/jenfi-mail-service/tree/develop/jenfimail/tests  
  
The models are strictly used for data access and schema design. It contains no logic at all.  
<b><i>models:</i></b> https://github.com/jjacarillo/jenfi-mail-service/blob/develop/jenfimail/models.py

All of business logic are in the services which serves as controller.   
<b><i>services:</i></b> https://github.com/jjacarillo/jenfi-mail-service/tree/develop/jenfimail/services</i></b>
en
### Optimization Solution  
https://github.com/jjacarillo/jenfi-mail-service/blob/develop/jenfimail/services/optimizer.py

[Jenfi Mail Service Optimization Documentation.pdf](https://github.com/jjacarillo/jenfi-mail-service/files/10273665/Jenfi.Mail.Service.Optimization.Documentation.pdf)

### Quick Setup
1. Install python 3 (3.9 or lower) -- use pyenv if you have different python versions
2. Clone repo
3. Install PostgresSQL and create database named `jenfi_test`
4. Inside project directory install dependencies and run migrations

```shell
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```
5. Run server
```shell
python manage.py runserver
```
This should start the app at port 8000

### Testing
Run unit tests  
```shell
python manage.py test
```
API endpoints:
http://127.0.0.1:8000/api/ - API index page  
For complete list of endpoints and usage see [test_api.py](https://github.com/jjacarillo/jenfi-mail-service/blob/develop/jenfimail/tests/test_api.py#L61)

REST endpoints: (not fully implemented)  
http://127.0.0.1:8000/lines/  
http://127.0.0.1:8000/trains/  
http://127.0.0.1:8000/parcels/  

You can test them out from the browser or using curl.


