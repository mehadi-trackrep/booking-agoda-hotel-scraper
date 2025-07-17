# Scrapy settings for scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scraper'
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

ROBOTSTXT_OBEY = False # Be careful and respectful when disabling this

# --- Django Integration ---
# import sys, os
# from pathlib import Path
# DJANGO_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent / 'django-project'
# sys.path.insert(0, str(DJANGO_PROJECT_ROOT))
# os.environ['DJANGO_SETTINGS_MODULE'] = 'django_project.settings'
# import django
# django.setup()

# --- Django Integration Settings ---
import os
import sys
from pathlib import Path

# 1. Calculate the absolute path to your Django project's root directory.
#    This is the directory that contains 'manage.py' and your main 'django_project' package.
#    Explanation based on your structure:
#    - Path(__file__).resolve() gives the absolute path to THIS settings.py file.
#      (e.g., /Users/md.mehadihasan/PERSONAL/@repositories/hotel-scrappery/scraper/scraper/settings.py)
#    - .parent (first) goes up to 'scraper/scraper/'
#    - .parent (second) goes up to 'scraper/'
#    - .parent (third) goes up to 'hotel-scrappery/'
#    - / 'django-project' appends the 'django-project' folder name.
DJANGO_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent / 'django-project'

# --- DEBUGGING PRINTS ---
print(f"\n--- Scrapy Django Integration Debugging ---")
print(f"Scrapy settings.py path: {Path(__file__).resolve()}")
print(f"Calculated DJANGO_PROJECT_ROOT: {DJANGO_PROJECT_ROOT}")
print(f"Does DJANGO_PROJECT_ROOT exist? {DJANGO_PROJECT_ROOT.exists()}")
print(f"Is DJANGO_PROJECT_ROOT a directory? {DJANGO_PROJECT_ROOT.is_dir()}")
print(f"--- End Scrapy Django Integration Debugging ---\n")
# --- END DEBUGGING PRINTS ---

# 2. Set the DJANGO_SETTINGS_MODULE environment variable FIRST.
#    This tells Django which settings file to use.
#    'django_project' is the name of your main Django project package.
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_project.settings' # Ensure 'django_project' is correct

# 3. Add the Django project's root directory to Python's system path.
#    This allows Python (and thus Django) to find your 'django_project' package.
sys.path.insert(0, str(DJANGO_PROJECT_ROOT))


# --- DEBUGGING PRINTS (after sys.path and environ changes) ---
print(f"\n--- Scrapy Django Integration Post-Path Debugging ---")
print(f"sys.path after insert: {sys.path[:3]}...") # Print first few elements
print(f"os.environ['DJANGO_SETTINGS_MODULE']: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
# Verify if django_project module can be imported now
try:
    import django_project.settings
    print(f"Successfully imported django_project.settings")
    # Also check if hotel_search is in INSTALLED_APPS from this context
    if 'hotel_search' in django_project.settings.INSTALLED_APPS:
        print(f"'hotel_search' found in INSTALLED_APPS.")
    else:
        print(f"WARNING: 'hotel_search' NOT found in INSTALLED_APPS from loaded settings.")
except ImportError as e:
    print(f"ERROR: Failed to import django_project.settings: {e}")
print(f"--- End Scrapy Django Integration Post-Path Debugging ---\n")
# --- END DEBUGGING PRINTS ---

# 4. Initialize Django.
#    This sets up Django's ORM and other components.
import django
django.setup()

ITEM_PIPELINES = {
   'scraper.pipelines.HotelScraperPipeline': 300,
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
DOWNLOAD_DELAY = 3 # Increase delay to be more respectful to servers
