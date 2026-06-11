import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os
import subprocess

from prefect import flow, task

DBT_PROJECT = ROOT / "dbt_demo" / "greenwheel"
DBT_PROFILES_DIR = ROOT / "docker" / "dbt"


def _dbt_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("DBT_POSTGRES_HOST", "localhost")
    env.setdefault("DBT_POSTGRES_PORT", "5432")
    env.setdefault("DBT_POSTGRES_USER", "dbt")
    env.setdefault("DBT_POSTGRES_PASSWORD", "dbt")
    env.setdefault("DBT_POSTGRES_DB", "dbt_demo")
    return env


@task(log_prints=True, retries=1, retry_delay_seconds=10)
def run_dbt(args: list[str]) -> None:
    command = ["dbt", *args, "--profiles-dir", str(DBT_PROFILES_DIR)]
    print(f"Running: {' '.join(command)}")
    subprocess.run(
        command,
        cwd=DBT_PROJECT,
        env=_dbt_env(),
        check=True,
    )


@flow(name="greenwheel-pipeline")
def greenwheel_pipeline() -> None:
    run_dbt(["seed"])
    run_dbt(["build"])


if __name__ == "__main__":
    greenwheel_pipeline()
