
# 🗓️ Week 11 — Deploy a Pipeline 🚀

Welcome to **Week 11** of *Learning in Public with dlt*!
This week, we’ll learn how to make your data pipeline run automatically — even when your computer is off.

You’ll learn how to:  
1️⃣ Deploy a pipeline using **GitHub Actions**  
2️⃣ Schedule and monitor it with **Apache Airflow**  
3️⃣ Handle **credentials** safely in both cases  

---

## 💡 Why Deploy?

When you deploy, your pipeline runs on its own — daily, hourly, or weekly — without manual effort.  
That’s what turns a small script into a **production-ready workflow**.

---

## ⚙️ Part 1 — Deploy with GitHub Actions

GitHub Actions lets you automate your workflow right inside GitHub.  
It’s like a virtual computer that wakes up on schedule, runs your code, and shuts down again.

### 🪄 Steps

#### 1️⃣ Test locally

Make sure your pipeline runs on your machine:

```bash
python your_pipeline.py
````

#### 2️⃣ Generate a workflow

```bash
pip install "dlt[cli]"
dlt deploy your_pipeline.py github-action --schedule "0 8 * * *"
```

This creates `.github/workflows/run_pipeline.yml`.

#### 3️⃣ Understand the workflow

```yaml
name: Run dlt pipeline
on:
  schedule:
    - cron: "0 8 * * *"      # every day at 8 AM UTC
  workflow_dispatch:          # manual trigger
jobs:
  run-dlt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - name: Install dependencies
        run: pip install "dlt[duckdb]" requests
      - name: Run pipeline
        run: python your_pipeline.py
```

#### 4️⃣ Add credentials

In **Settings → Secrets → Actions**, add secrets like:

```
DESTINATION__BIGQUERY__CREDENTIALS__PROJECT_ID
DESTINATION__BIGQUERY__CREDENTIALS__PRIVATE_KEY
SOURCES__PIPEDRIVE__PIPEDRIVE_API_KEY
```

Then reference them in the YAML:

```yaml
env:
  DESTINATION__BIGQUERY__CREDENTIALS__PRIVATE_KEY: ${{ secrets.DESTINATION__BIGQUERY__CREDENTIALS__PRIVATE_KEY }}
```

#### 5️⃣ Push and monitor

Commit → push → open the **Actions** tab → watch your workflow run and check logs.

---

## 🔐 Handling Credentials Locally

When working locally, dlt looks for credentials in:

```
.dlt/secrets.toml
```

Example:

```toml
[sources.pipedrive]
pipedrive_api_key = "your_api_key"

[destination.bigquery.credentials]
project_id = "project_id"
private_key = "private_key"
client_email = "client_email"
```

When deployed, the same structure works through **environment variables** — just replace dots with `__` and use uppercase names.

---

## 🎛️ Part 2 — Schedule with Apache Airflow

Airflow lets you **orchestrate** and **visualize** your pipelines.
You write a simple Python file (called a DAG), and Airflow runs it automatically.

### Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import dlt, requests

def run_pipeline():
    @dlt.resource(write_disposition="replace")
    def launches():
        url = "https://ll.thespacedevs.com/2.0.0/launch/upcoming"
        yield requests.get(url).json()

    p = dlt.pipeline("spacedevs_pipeline", destination="duckdb", dataset_name="launches")
    p.run(launches())

with DAG(
    "11_spacedevs_daily",
    start_date=datetime(2025,10,1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    run = PythonOperator(task_id="run_dlt_pipeline", python_callable=run_pipeline)
```

### Run Airflow

```bash
airflow db migrate
airflow standalone
```

Then open [http://localhost:8080](http://localhost:8080), enable your DAG, and watch your pipeline run automatically.
You can see logs, retries, and history — all from one dashboard.

---

## 🧠 Wrap-Up

| Tool               | Purpose                           | When to Use          |
| ------------------ | --------------------------------- | -------------------- |
| **GitHub Actions** | Simple automation in the cloud    | Daily or hourly jobs |
| **Apache Airflow** | Full orchestration and monitoring | Complex pipelines    |

---

## 🌐 Next Steps — Explore More Deployment Options

dlt supports many other ways to deploy — from **Google Cloud Run** to **Prefect**, **Dagster**, **Kestra**, and more.
If you’d like to see all 11 deployment options, check them out here:

👉 **[dlt Docs — Deploying Pipelines](https://dlthub.com/docs/walkthroughs/deploy-a-pipeline)**

---

✨ You now have a pipeline that can run by itself — every day, on time, and safely.
Next week: **Running in Production & Monitoring Pipelines Like a Pro.**

📍 [View Repo → github.com/1997mahadi/Data-Engineering-with-dlt](https://github.com/1997mahadi/Data-Engineering-with-dlt/tree/main)

```