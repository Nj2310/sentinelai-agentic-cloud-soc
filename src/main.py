
from src.soc_pipeline import run_soc_pipeline


def main():
    """Launch the SentinelAI unified SOC pipeline."""

    print("=" * 60)
    print("SentinelAI - Agentic AI Cloud Security Operations")
    print("=" * 60)
    print("Mode: Local SOC Investigation")
    print("Data Source: Synthetic AWS CloudTrail Logs")
    print("Investigation Policy: Controlled Read-Only")
    print("=" * 60)

    results = run_soc_pipeline()

    print("\nSOC pipeline execution finished.")
    print(f"Run ID: {results['run_id']}")
    print(
        f"Total alerts: "
        f"{results['summary']['total_alerts']}"
    )

    print("\nTo view the SOC dashboard, run:")
    print("python -m streamlit run dashboard/app.py")


if __name__ == "__main__":
    main()