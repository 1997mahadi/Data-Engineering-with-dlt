from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime
import dlt
from dlt.common import Decimal


@dlt.resource(primary_key="id")
def customers():
    yield [
        {"id": 1, "name": "simon", "city": "berlin"},
        {"id": 2, "name": "violet", "city": "london"},
        {"id": 3, "name": "tammo", "city": "new york"},
    ]


@dlt.resource(primary_key="id")
def inventory():
    yield [
        {"id": 1, "name": "apple", "price": Decimal("1.50")},
        {"id": 2, "name": "banana", "price": Decimal("1.70")},
        {"id": 3, "name": "pear", "price": Decimal("2.50")},
    ]


@dlt.source
def fruitshop_source(start_date):
    return customers(), inventory()


def run_dlt_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="fruitshop_pipeline",
        destination="duckdb",
        dataset_name="fruitshop_data"
    )
    info = pipeline.run(fruitshop_source(start_date="2025-01-01"))
    print(pipeline.default_schema.to_pretty_yaml())
    print(info)


with DAG(
    dag_id="10_fruitshop_dlt_airflow",
    start_date=datetime(2025, 10, 1),
    schedule=None,
    catchup=False,
    description="Week 10: dlt schema + Airflow (Part 2)"
) as dag:

    start = DummyOperator(task_id="start")
    run_pipeline = PythonOperator(
        task_id="run_dlt_pipeline",
        python_callable=run_dlt_pipeline
    )
    end = DummyOperator(task_id="end")

    start >> run_pipeline >> end
