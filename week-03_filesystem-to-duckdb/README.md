📦 Week 03 – Loading Files from Local or Cloud Storage with dlt 🚀

Welcome to Week 3 of the **"Data Engineering with dlt"** educational series.

This week, we’re shifting gears to one of the most common data engineering tasks:

> ✅ Reading raw files (like CSV, JSONL, or Parquet) from your **local machine** or a **cloud bucket**, and transforming them into clean, structured datasets using `dlt`.

---

## 📚 What You’ll Learn This Week

By the end of this lesson, you’ll be able to:

- Connect to local or cloud-based storage (like Google Cloud Storage)
- Use `dlt.sources.filesystem` to discover and read multiple files at once
- Transform CSV files into clean Python records
- Load your data into **DuckDB** (a local analytics database)
- Add metadata (like filename or path) to your loaded data
- Run your pipeline again — and only load **new or modified** files (incremental load)

---

## 🛠️ Step-by-Step Setup

### 1️⃣ Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
````

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```txt
dlt[duckdb]
pandas
```

> Optionally add `streamlit` if you want to explore the results visually.

---

## 📂 Folder Contents

| File                     | Purpose                                     |
| ------------------------ | ------------------------------------------- |
| `filesystem_pipeline.py` | Main pipeline loading CSVs from local/cloud |
| `requirements.txt`       | Project dependencies                        |
| `.dlt/config.toml`       | Configuration for your pipeline             |
| `.dlt/secrets.toml`      | Secrets like GCP credentials (if needed)    |
| `README.md`              | You’re reading it now 🙂                    |

---

## 🧠 Key Concepts

### 🔸 `filesystem()`

This dlt helper allows you to:

* List all files in a folder (local or cloud)
* Apply a filter using `file_glob="*.csv"` or similar

### 🔸 `read_csv()`

This transformer parses each file into structured Python records.

### 🔸 `pipeline.run()` with `write_disposition`

How you load data:

* `append`: keep adding new rows
* `replace`: delete existing table and reload
* `merge`: deduplicate using a key
* `incremental`: only load new files or rows

---

## 🐍 Example Pipeline Code

```python
from typing import Any, Iterator
import dlt
from dlt.sources import TDataItems
from dlt.sources.filesystem import FileItemDict
from dlt.sources.filesystem import filesystem

@dlt.transformer()
def read_csv_custom(items: Iterator[FileItemDict], chunksize: int = 10000, **pandas_kwargs: Any) -> Iterator[TDataItems]:
    import pandas as pd
    import uuid

    kwargs = {**{"header": "infer", "chunksize": chunksize}, **pandas_kwargs}

    for file_obj in items:
        with file_obj.open() as file:
            for df in pd.read_csv(file, **kwargs):
                df["file_name"] = file_obj["file_name"]
                df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]  # Generate unique ID
                yield df.to_dict(orient="records")

# Select JSON or CSV files
files = filesystem(file_glob="encounters*.csv")
files.apply_hints(incremental=dlt.sources.incremental("modification_date"))

reader = (files | read_csv_custom()).with_name("encounters")
reader.apply_hints(primary_key="id", incremental=dlt.sources.incremental("STOP"))

pipeline = dlt.pipeline(
    pipeline_name="filesystem_pipeline",  # or match with `hospital_data_pipeline` if using that name
    dataset_name="hospital_data",
    destination="duckdb",
    dev_mode=False  # recommended instead of deprecated full_refresh
)

info = pipeline.run(reader, write_disposition="merge")
print(info)
```

---

## 🧪 Run the Pipeline

```bash
python filesystem_pipeline.py
```

Your data will be loaded into `filesystem_pipeline.duckdb` and enriched with metadata.

To view the data visually:

```bash
pip install streamlit
dlt pipeline filesystem_pipeline show
```

---

## ☁️ Want to Use Cloud Storage?

Edit your `.dlt/secrets.toml` like this:

```toml
[sources.filesystem.credentials]
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
project_id = "your-project-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

And change the `bucket_url` to:

```python
bucket_url="gs://your-bucket-name"
```

---

## 🧠 Recap: Why This Matters

Loading data from files is **the first step** in most real-world data workflows.

With `dlt`, you can:

* Build pipelines that scale from your laptop to the cloud
* Switch between local dev and production with no code changes
* Add rich metadata, schema inference, and logging for free

---

## 📌 Next Steps

In **Week 4**, we’ll go even further — creating a **custom dlt source** that combines all you’ve learned so far (files + transformations + logic)!

Follow along on [LinkedIn](https://www.linkedin.com/company/phitau-digital)

---

## 🧵 Share your progress!

If you're learning with us, tag your posts with `#dlt #learninginpublic #dataengineering`

---

\#dlt #duckdb #python #dataengineering #etl #filesystem #opensource #learninginpublic

