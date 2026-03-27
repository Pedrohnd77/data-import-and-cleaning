"""
Airflow DAG: NBA Stats EDA Pipeline
====================================
Source repo : https://github.com/Pedrohnd77/nba-stats-eda
Trigger     : Manual (schedule_interval=None)
Author      : Pedro Henrique Domingos

Pipeline tasks:
  1. pull_repo_from_github  → Clone or update the repo
  2. validate_data_files    → Check that the CSV files exist in data/
  3. run_nba_eda_analysis   → Execute the converted Python script
  4. list_outputs           → Print the generated output files
"""

from datetime import timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# ---------------------------------------------------------------------------
# Paths inside the Docker containers
# ---------------------------------------------------------------------------
GITHUB_REPO  = "https://github.com/Pedrohnd77/nba-stats-eda.git"
REPO_DIR     = "/opt/airflow/repo/nba-stats-eda"
DATA_PATH    = "/opt/airflow/data"
OUTPUT_PATH  = "/opt/airflow/outputs"
SCRIPT_PATH  = "/opt/airflow/dags/scripts/nba_stats_eda.py"

# ---------------------------------------------------------------------------
# Default arguments applied to every task
# ---------------------------------------------------------------------------
default_args = {
    'owner':            'pedro',
    'depends_on_past':  False,
    'email_on_failure': False,
    'email_on_retry':   False,
    'retries':          1,
    'retry_delay':      timedelta(minutes=2),
}

# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------
with DAG(
    dag_id          = 'nba_stats_eda_pipeline',
    description     = 'EDA pipeline for NBA 2022-2023 player stats (manual trigger)',
    default_args    = default_args,
    schedule_interval = None,          # ← Manual trigger only (no automatic schedule)
    start_date      = days_ago(1),
    catchup         = False,
    tags            = ['nba', 'eda', 'data-pipeline'],
) as dag:

    # -----------------------------------------------------------------------
    # TASK 1 — Pull the latest code from GitHub
    # -----------------------------------------------------------------------
    pull_repo = BashOperator(
        task_id='pull_repo_from_github',
        bash_command='echo "Código disponível via volume mount local — git pull ignorado em dev."',
    )

    # -----------------------------------------------------------------------
    # TASK 2 — Validate that the required CSV data files are present
    # -----------------------------------------------------------------------
    validate_data = BashOperator(
        task_id     = 'validate_data_files',
        bash_command = f"""
            echo "=== TASK 2: Validate data files ==="

            REGULAR="{DATA_PATH}/2022-2023 NBA Player Stats - Regular.csv"
            PLAYOFFS="{DATA_PATH}/2022-2023 NBA Player Stats - Playoffs.csv"

            if [ ! -f "$REGULAR" ]; then
                echo "ERROR: Regular season CSV not found!"
                echo "Expected location: $REGULAR"
                echo ""
                echo "SOLUTION: Place the CSV files inside the data/ folder"
                echo "  └── nba-airflow-pipeline/"
                echo "        └── data/"
                echo "              ├── 2022-2023 NBA Player Stats - Regular.csv"
                echo "              └── 2022-2023 NBA Player Stats - Playoffs.csv"
                echo ""
                echo "Download from: https://www.kaggle.com/datasets/vivovinco/20222023-nba-player-stats-regular"
                exit 1
            fi

            if [ ! -f "$PLAYOFFS" ]; then
                echo "ERROR: Playoffs CSV not found!"
                echo "Expected location: $PLAYOFFS"
                exit 1
            fi

            echo "✅ Both data files found. Proceeding..."
            wc -l "$REGULAR"
            wc -l "$PLAYOFFS"
        """,
    )

    # -----------------------------------------------------------------------
    # TASK 3 — Run the EDA analysis script
    # -----------------------------------------------------------------------
    run_analysis = BashOperator(
        task_id     = 'run_nba_eda_analysis',
        bash_command = f"""
            echo "=== TASK 3: Run NBA EDA Analysis ==="
            mkdir -p {OUTPUT_PATH}

            NBA_DATA_PATH={DATA_PATH} \
            NBA_OUTPUT_PATH={OUTPUT_PATH} \
            python {SCRIPT_PATH}

            echo "Analysis script finished with exit code: $?"
        """,
        env = {
            'NBA_DATA_PATH':   DATA_PATH,
            'NBA_OUTPUT_PATH': OUTPUT_PATH,
        },
    )

    # -----------------------------------------------------------------------
    # TASK 4 — List generated output files
    # -----------------------------------------------------------------------
    list_outputs = BashOperator(
        task_id     = 'list_outputs',
        bash_command = f"""
            echo "=== TASK 4: Generated Outputs ==="
            echo ""
            echo "Files saved to: {OUTPUT_PATH}"
            echo ""
            ls -lh {OUTPUT_PATH}/ 2>/dev/null || echo "(no files found)"
            echo ""
            echo "✅ Pipeline completed!"
        """,
    )

    # -----------------------------------------------------------------------
    # Task dependency chain: 1 → 2 → 3 → 4
    # -----------------------------------------------------------------------
    pull_repo >> validate_data >> run_analysis >> list_outputs