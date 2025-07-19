It is an simple but highly effective hotel search web app which fetches the hotel info from booking.com and agoda based on user input and shows the best matches.
Tech stacks - Django, Requests, Scrapy, Celery, Redis broker.

### ER diagram public link - https://dbdiagram.io/d/hotel_search_erd-687128b4f413ba3508757786


### Installation 🛠️
* Install uv
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
* Create virtual env
```
uv venv
```
* Install dependencies from uv.lock file
```
uv sync
```
* 



### dd

* sudo docker-compose up db --build -d [only for database]
* sudo docker-compose exec db psql -U hotel_user -d hotel_db
* sudo docker-compose down -v


[dev commands]
## If we face database migration issues then run - 
bash clean_pycache.sh

1.  sudo docker-compose up db --build -d
    sudo docker-compose exec db psql -U hotel_user -d hotel_db
    sudo docker-compose down -v

2.  cd django-project
    uv run python manage.py makemigrations hotel_search
    uv run python manage.py migrate

3. uvicorn app.main:app --port 8001 --reload --log-level debug

## To run the project
1. sudo docker-compose up db --build -d
2. uv run python manage.py runserver
3. go to the 'http://127.0.0.1:8000/search/' link.
4. uvicorn app.main:app --port 8001 --reload
4. use postman & hit - http://127.0.0.1:8001/api/search_hotels

```
        curl -X POST http://127.0.0.1:8001/api/search_hotels \
        -H "Content-Type: application/json" \
        -d '{"city": "Bangkok", "min_price": 50, "max_price": 300, "rating": 4.0}'

```