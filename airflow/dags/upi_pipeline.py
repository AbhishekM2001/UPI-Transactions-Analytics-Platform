from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

# Our cookie recipe book
with DAG(
    "upi_pipeline", start_date=datetime(2023, 1, 1), schedule_interval="@monthly"
) as dag:
    # Step 1: Get ingredients (scrape RBI website)
    scrape = BashOperator(
        task_id="scrape", bash_command="python /app/scripts/scrape.py"
    )

    # Step 2: Mix dough (clean data)
    clean = BashOperator(task_id="clean", bash_command="python /app/scripts/clean.py")

    # Step 3: Bake cookies (upload to GCS)
    upload = BashOperator(
        task_id="upload", bash_command="python /app/scripts/upload.py"
    )

    # Step 4: Add sprinkles (refresh views)
    refresh = BashOperator(
        task_id="refresh", bash_command="python /app/scripts/refresh.py"
    )

    # Proper cookie-making order
    scrape >> clean >> upload >> refresh
