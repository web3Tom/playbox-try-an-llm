"""
Pandas-based data analysis and visualization demo.

Reads transaction metrics, computes rolling averages, and generates a chart.
Can be executed directly or via Kilo Code for dynamic analysis workflows.

Dependencies: pandas, matplotlib
"""

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_report(input_file: str = "demos/data-analysis/transaction_metrics.csv",
                     output_file: str = "output_chart.png"):
    """Read CSV, compute rolling average, and generate chart."""
    try:
        logger.info(f"Reading data from {input_file}...")
        df = pd.read_csv(input_file)
        logger.info(f"Loaded {len(df)} rows")

        df['rolling_avg_volume'] = df['transaction_volume_usd'].rolling(window=7).mean()

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['date'], df['transaction_volume_usd'], label='Daily Volume (USD)', marker='o')
        ax.plot(df['date'], df['rolling_avg_volume'], label='7-Day Rolling Average', linestyle='--', linewidth=2)
        ax.set_xlabel('Date')
        ax.set_ylabel('Transaction Volume (USD)')
        ax.set_title('Daily vs 7-Day Rolling Average Transaction Volume')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        logger.info(f"Saving chart to {output_file}...")
        plt.savefig(output_file, dpi=150)
        logger.info(f"Chart saved: {output_file}")
        print(f"✓ Report generated: {output_file}")

    except FileNotFoundError as e:
        logger.error(f"File not found: {input_file}")
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise


if __name__ == "__main__":
    generate_report()
