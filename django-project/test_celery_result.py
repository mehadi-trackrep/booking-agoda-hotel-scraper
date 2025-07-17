import os
from celery import Celery
from celery.result import AsyncResult



# --- Configuration for your Celery app ---
# This part is crucial: your script needs to know how to connect to Celery's broker and backend.
# It should mirror the configuration in your Django project's settings.py and celery.py.

# Set the default Django settings module for the 'celery' program.
# This assumes your Django project's main settings are in 'django_project.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

# Initialize the Celery app (replace 'django_project' with your actual Celery app name)
app = Celery('django_project')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Ensure tasks are auto-discovered (though not strictly necessary for just getting results)
app.autodiscover_tasks()

# --- End Celery app configuration ---


def get_celery_task_result(task_id_str):
    """
    Retrieves the result of a Celery task given its ID.
    """
    print(f"Attempting to retrieve result for task ID: {task_id_str}")
    
    # Create an AsyncResult object for the given task ID
    task_result = AsyncResult(task_id_str, app=app) # Pass the app instance

    # Check the status of the task
    print(f"Task status: {task_result.status}")

    if task_result.ready(): # Check if the task has completed (success or failure)
        try:
            # .get() will retrieve the result. If the task failed, it will re-raise the exception.
            result_data = task_result.get() 
            print("Task completed successfully. Result:")
            print(result_data)
            return result_data
        except Exception as e:
            print(f"Task failed with an exception: {e}")
            print(f"Task traceback:\n{task_result.traceback}") # Get the traceback if available
            return None
    else:
        print("Task is not yet ready (still PENDING or STARTED).")
        return None


if __name__ == "__main__":
    # Replace with the actual task ID you want to retrieve
    # This should be the group task ID that you get from run_spiders_for_query.delay().id
    target_task_id = "fe10e6fd-6834-4f4b-8c7c-6e10e81022f7" 

    # Example usage:
    # If you want to test with a known good task ID from your logs, paste it here.
    # For example: "62a13f8e-07c5-47e4-a221-d78d0f721d30" (from your error log, assuming it was a group ID)
    
    # IMPORTANT: Ensure your Celery broker (Redis) is running when you run this script.
    # Also, ensure your Celery worker has processed the task.

    result = get_celery_task_result(target_task_id)

    if result:
        print("\n--- Processed Result ---")
        # If your group task returns a list of dictionaries (from individual_spider_task),
        # you can process them here.
        # Example:
        # for subtask_res in result:
        #     if subtask_res.get('status') == 'SUCCESS':
        #         print(f"Subtask {subtask_res.get('task_id')} succeeded.")
        #     else:
        #         print(f"Subtask {subtask_res.get('task_id')} failed: {subtask_res.get('error')}")