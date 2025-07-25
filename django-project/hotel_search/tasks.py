# django-project/hotel_search/tasks.py
from celery import shared_task, group
import subprocess
import os
from django.conf import settings
from pathlib import Path
from datetime import datetime


@shared_task(bind=True)
def individual_spider_task(self, spider_name, city, price=None, rating=None, checkin=None, agoda_city_id=None):
    """
    A Celery task to run a single Scrapy spider with arguments.
    It now passes the GROUP task ID (self.request.root_id) to the spider.
    """

    individual_task_id = self.request.id # Get the ID of the individual task (for subprocess command)
    group_task_id = self.request.root_id # Get the ID of the group task (root task)

    scraper_project_path = Path(settings.BASE_DIR).parent / 'scraper'

    print(f"DEBUG: Attempting to use Scrapy project path: {scraper_project_path}")
    if not scraper_project_path.exists():
        error_msg = f"ERROR: Scrapy project path DOES NOT EXIST: {scraper_project_path}"
        print(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'task_id': individual_task_id, 'status': 'FAILURE', 'error': error_msg}
    if not scraper_project_path.is_dir():
        error_msg = f"ERROR: Scrapy project path is not a directory: {scraper_project_path}"
        print(error_msg)
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'task_id': individual_task_id, 'status': 'FAILURE', 'error': error_msg}

    command = [
        'scrapy', 'crawl', spider_name,
        '-a', f'city={city}',
        '-a', f'search_task_id={group_task_id}', # Pass the GROUP task ID to the spider as 'search_task_id'
        '-a', f'individual_task_id={individual_task_id}' 
    ]

    if price:
        command.extend(['-a', f'price={price}'])
    if rating:
        command.extend(['-a', f'rating={rating}'])
    if checkin:
        command.extend(['-a', f'checkin={checkin}'])
    if agoda_city_id:
        command.extend(['-a', f'agoda_city_id={agoda_city_id}'])

    print(f"Executing command for {spider_name}: {' '.join(command)} in {scraper_project_path}")

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'django_project.settings'
    django_project_root = Path(settings.BASE_DIR).parent
    env['PYTHONPATH'] = str(django_project_root) + os.pathsep + env.get('PYTHONPATH', '')
    venv_bin_path = Path(settings.BASE_DIR).parent / '.venv' / 'bin'
    env['PATH'] = str(venv_bin_path) + os.pathsep + env.get('PATH', '')

    try:
        result = subprocess.run(
            command,
            cwd=scraper_project_path,
            env=env,
            check=True,
            capture_output=True,
            text=True,
            shell=False
        )
        print(f"Spider {spider_name} stdout:\n{result.stdout}")
        if result.stderr:
            print(f"Spider {spider_name} stderr:\n{result.stderr}")
        
        self.update_state(state='SUCCESS', meta={'task_id': individual_task_id, 'spider_name': spider_name})
        return {'task_id': individual_task_id, 'status': 'SUCCESS', 'spider_name': spider_name}
    except subprocess.CalledProcessError as e:
        scrapy_output_error = (
            f"Scrapy Command: {' '.join(e.cmd)}\n"
            f"Scrapy Exit Status: {e.returncode}\n"
            f"Scrapy STDOUT:\n{e.stdout}\n"
            f"Scrapy STDERR:\n{e.stderr}"
        )
        error_msg = f"Error running {spider_name} for task {individual_task_id}:\n{scrapy_output_error}"
        print(f"ERROR: {error_msg}")
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'task_id': individual_task_id, 'status': 'FAILURE', 'error': error_msg}
    except FileNotFoundError as e:
        error_msg = f"Command 'scrapy' not found. Is Scrapy installed and in PATH? Error: {e}"
        print(f"ERROR: {error_msg}")
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'task_id': individual_task_id, 'status': 'FAILURE', 'error': error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred for {spider_name} task {individual_task_id}: {e}"
        print(f"ERROR: {error_msg}")
        self.update_state(state='FAILURE', meta={'error': error_msg})
        return {'task_id': individual_task_id, 'status': 'FAILURE', 'error': error_msg}


@shared_task
def run_spiders_for_query(city,  price=None, rating=None, agoda_city_id=None):
    """
    Creates a group of Celery tasks to run all spiders for a given search query.
    """
    print(f"Initiating spider group for city: {city}")
    current_datetime = datetime.now()
    # Format the date as YYYY-MM-DD
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    
    booking_signature = individual_spider_task.s('booking_spider', city, price=price, rating=rating, checkin=formatted_date)
    agoda_signature = individual_spider_task.s('agoda_spider', city, price=price, rating=rating, checkin=formatted_date, agoda_city_id=agoda_city_id)

    task_group = group(booking_signature, agoda_signature)
    # task_group = group(agoda_signature, )
    
    result = task_group.apply_async()
    
    print(f"Group task initiated with ID: {result.id}")
    return result.id
