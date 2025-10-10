# 🧩 Week 10 — Schema in dlt + Airflow (Part 2)

Welcome to **Week 10** of our *Learning in Public with dlt* journey!
This week, we explore two connected ideas:

1. **Schema in dlt** — how dlt understands, organizes, and evolves your data.
2. **Airflow (Part 2)** — a gentle continuation showing how to run a dlt pipeline as a task in Airflow.

---

## 🧠 1) What is a Schema in dlt?

A **schema** is like your pipeline’s memory of how the data is structured — its *blueprint*.
It tells dlt what tables exist, which columns they have, and what type of values each column contains.

Every time you run a pipeline, dlt examines the data you load and automatically creates or updates a schema to match it.
That means you don’t need to manually design tables — dlt learns their shape from the data itself.

> 🟢 Think of it as “data self-organization” — dlt sees your Python dictionaries and turns them into structured tables in DuckDB (or any destination).

### Why schemas matter

* They make your data consistent and queryable.
* They evolve safely when the structure changes (e.g., a new column appears).
* They let you control how columns are typed or renamed.
* They help with incremental loads by keeping track of what’s already in the destination.

---

## 📊 2) How dlt builds schemas automatically

When you run a pipeline, dlt scans the data you yield and creates tables accordingly.

Example:

```python
import dlt

@dlt.resource
def fruitshop():
    yield [
        {"id": 1, "fruit": "apple", "price": 1.5},
        {"id": 2, "fruit": "banana", "price": 1.2},
    ]

p = dlt.pipeline(
    pipeline_name="fruitshop_pipeline",
    destination="duckdb",
    dataset_name="fruitshop_data"
)
p.run(fruitshop())
```

The schema it creates looks like this (internally):

```yaml
tables:
  fruitshop:
    columns:
      id:
        data_type: bigint
      fruit:
        data_type: text
      price:
        data_type: double
```

dlt detects types ( `bigint`, `text`, `double` ) by looking at the data it sees in each column.

---

## 🧩 3) Enriching the schema — multiple resources and type hints

Schemas can combine multiple resources into one logical source.
Let’s use a small example with two resources that belong to the same “fruitshop” source.

```python
import dlt
from dlt.common import Decimal


@dlt.resource(primary_key="id")
def customers():
    """Load customer data from a simple python list."""
    yield [
        {"id": 1, "name": "simon", "city": "berlin"},
        {"id": 2, "name": "violet", "city": "london"},
        {"id": 3, "name": "tammo", "city": "new york"},
    ]


@dlt.resource(primary_key="id")
def inventory():
    """Load inventory data from a simple python list."""
    yield [
        {"id": 1, "name": "apple", "price": Decimal("1.50")},
        {"id": 2, "name": "banana", "price": Decimal("1.70")},
        {"id": 3, "name": "pear", "price": Decimal("2.50")},
    ]


@dlt.source
def fruitshop_source(start_date):
    """A source function groups all resources into one schema."""
    return customers(), inventory()
```

Now our schema has two tables (`customers` and `inventory`) under one dataset.
Each has its own columns, primary keys, and data types inferred automatically.

---

## 🔍 4) Viewing the schema that dlt generated

You can see the exact schema using:

```python
print(p.default_schema.to_pretty_yaml())
```

It prints a clean YAML view of your schema showing all tables, columns, and types.
You can also open the schema file in:
`~/.dlt/pipelines/<pipeline_name>/schemas/`

---

## 🧠 5) Adjusting and controlling schemas (gently)

You can guide dlt by adding small **type hints** or **rules**, for example:

```python
@dlt.resource(
    name="inventory",
    columns={
        "price": {"data_type": "double", "nullable": False}
    }
)
def inventory():
    yield [{"id": 1, "name": "apple", "price": 1.5}]
```

You can also decide how column names are formatted (using snake_case by default), or keep original names via a config like this in `config.toml`:

```toml
[schema]
naming = "direct"
```

Most of the time, you don’t need to change anything — but knowing these options gives you control when your data grows more complex.

---

## ⚙️ 6) Airflow — Orchestrating the Pipeline (Part 2)

We introduced Airflow in Week 9.
If you haven’t set it up yet, please follow the **Week 9 setup instructions** first and come back here.

### What is Airflow (quick recap)

[Apache Airflow](https://airflow.apache.org/) is an open-source platform for **orchestrating data workflows**.
It lets you define and visualize tasks as a graph (DAG = Directed Acyclic Graph).
Each task is a small step in a data workflow — like *run a pipeline*, *send a notification*, *transform a table*, etc.

Here’s how it works in our case:

* Each DAG is a Python file.
* Inside it, we define tasks (`start`, `run_dlt_pipeline`, `end`).
* Airflow executes them in order and lets you monitor success or failure visually from the web UI.

### Our simple DAG for Week 10

This Airflow DAG runs the `fruitshop_source()` and loads it into DuckDB.

**File:** `dags/fruitshop_dlt_dag.py`

```python
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
```

You can drop this file into your Airflow `dags/` folder and trigger it exactly like in Week 9.
It will run your dlt pipeline, load data to DuckDB, and print the generated schema in the logs.

---

## 🗂️ Repo structure (for GitHub)

```
week-10_schema/
│── README.md
│── requirements.txt
│── dags/
│    └── fruitshop_dlt_dag.py
```



## ✅ Wrap-up

* A **schema** is the blueprint of your data — dlt creates and updates it for you.
* You can **inspect**, **enrich**, and **control** schemas easily with a few lines of code.
* Airflow lets you **orchestrate** these pipelines and see them visually as tasks.

👉 If you haven’t done Week 9 yet, check it first for the Airflow setup steps before running this lesson.

