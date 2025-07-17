from hotel_search.tasks import individual_spider_task, group
from celery.result import AsyncResult
from django_project.celery import app # Assuming your Celery app is named django_project

# Create dummy tasks (they don't need to actually run, but need to be defined)
# These are just signatures, not actual executions yet
task1_sig = individual_spider_task.s('dummy_spider1', 'city1', 'price1', 'rating1')
task2_sig = individual_spider_task.s('dummy_spider2', 'city2', 'price2', 'rating2')

# Create a group
test_group = group(task1_sig, task2_sig)

# Apply it asynchronously
group_result = test_group.apply_async()
print(f"Group task ID: {group_result.id}")

print("Waiting for group task to complete... (Ensure Celery worker is running)")

# Poll its status until ready (or timeout after a few seconds)
import time
timeout_seconds = 30 # Adjust as needed
start_time = time.time()
while not group_result.ready() and (time.time() - start_time < timeout_seconds):
    print(f"Status: {group_result.status}")
    time.sleep(2) # Wait 2 seconds

if not group_result.ready():
    print("Group task did not complete within the timeout. Check Celery worker logs.")

try:
    results_from_get = group_result.get()
    print(f"\n--- Shell Test Results ---")
    print(f"Type of results_from_get: {type(results_from_get)}")
    print(f"Content of results_from_get: {results_from_get}")
    print(f"--- End Shell Test Results ---")
except Exception as e:
    print(f"\n--- Shell Test Error ---")
    print(f"Error calling get() on group result: {e}")
    print(f"--- End Shell Test Error ---")