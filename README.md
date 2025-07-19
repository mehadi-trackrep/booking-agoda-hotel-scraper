It is an simple but highly effective hotel search web app which fetches the hotel info from booking.com and agoda based on user input and shows the best matches.
Tech stacks - Django, Requests, Scrapy, Celery, Redis broker.


### Installation 🛠️
* Install uv
```
curl -LsSf https://astral.sh/uv/install.sh | sh
OR
pip install uv
OR
pip install uv
```
* Create virtual env
```
uv venv
```
* Install dependencies from uv.lock file
```
uv sync
```

### 🚀 Quick Start
We can run the four or three commands in different terminal windows.
```
    sudo docker-compose up db redis --build -d

    cd django-project

    # run the following commands in the djanog-project directory path
    celery -A django_project worker --loglevel=info`
    uv run python manage.py runserver
    
    go to the 'http://127.0.0.1:8000/

```


### [dev commands]
```
# If we face database migration issues then run - 
bash clean_pycache.sh

1.  sudo docker-compose up db --build -d  [only for database]
    sudo docker-compose exec db psql -U hotel_user -d hotel_db
    sudo docker-compose down -v

2.  cd django-project
    uv run python manage.py makemigrations hotel_search
    uv run python manage.py migrate
```

### ** ER diagram public link - https://dbdiagram.io/d/hotel_search_erd-687128b4f413ba3508757786

##### Before login required
```
        curl -X POST http://127.0.0.1:8001/api/search_hotels \
        -H "Content-Type: application/json" \
        -d '{"city": "Bangkok", "min_price": 50, "max_price": 300, "rating": 4.0}'

```