import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from jinja2 import Environment, FileSystemLoader


class ReportGenerator:
    """Generates Markdown and JSON reports from evaluation results.

    This module aggregates data from metrics, model answers, and experiment
    configuration to produce human-readable and machine-processable reports.
    """

    def __init__(
        self,
        metrics_path: Path,
        answers_path: Path,
        config: Dict[str, Any],
        output_dir: Path,
        template_dir: Optional[Path] = None,
    ):
        """Initializes the ReportGenerator.

        Args:
            metrics_path: Path to the CSV file containing evaluation metrics.
            answers_path: Path to the CSV file containing model answers.
            config: Dictionary containing the experiment configuration.
            output_dir: Directory where the reports will be saved.
            template_dir: Optional path to the directory containing Jinja2 templates.
        """
        self.metrics_path = Path(metrics_path)
        self.answers_path = Path(answers_path)
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = template_dir

        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    def load_data(self) -> pd.DataFrame:
        """Loads and merges metrics and answers data.

        Returns:
            A pandas DataFrame containing the merged data.
        """
        metrics_df = pd.read_csv(self.metrics_path)
        answers_df = pd.read_csv(self.answers_path)

        # Assuming 'id' or 'question_id' is the common column
        merge_col = "id" if "id" in metrics_df.columns else "question_id"
        return pd.merge(metrics_df, answers_df, on=merge_col, suffixes=("_metric", "_answer"))

    def aggregate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates summary statistics and aggregated metrics.

        Args:
            df: The merged DataFrame.

        Returns:
            A dictionary containing aggregated metrics.
        """
        summary = {
            "model_name": self.config.get("model", {}).get("name", "Unknown"),
            "total_samples": len(df),
            "metrics": {},
        }

        # Example: Calculate mean for all numeric metric columns
        metric_cols = [c for c in df.columns if c.endswith("_metric") or c in ["accuracy", "f1", "latency"]]
        for col in metric_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                summary["metrics"][col] = {
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "p95": df[col].quantile(0.95),
                    "p99": df[col].quantile(0.99),
                }

        return summary

    def generate_markdown(self, summary: Dict[str, Any], template_name: str = "report.md.j2") -> Path:
        """Generates a Markdown report using Jinja2.

        Args:
            summary: The aggregated metrics dictionary.
            template_name: The name of the template file.

        Returns:
            The path to the generated Markdown report.
        """
        template = self.env.get_template(template_name)
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_text = template.render(
            summary=summary,
            config=self.config,
            report_date=report_date
        )

        report_path = self.output_dir / "final_report.md"
        report_path.write_text(output_text, encoding="utf-8")
        return report_path

    def generate_json(self, summary: Dict[str, Any]) -> Path:
        """Generates a JSON report for analytics.

        Args:
            summary: The aggregated metrics dictionary.

        Returns:
            The path to the generated JSON report.
        """
        json_path = self.output_dir / "report_data.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        return json_path

    def run(self):
        """Executes the full reporting pipeline."""
        df = self.load_data()
        summary = self.aggregate_metrics(df)
        self.generate_markdown(summary)
        self.generate_json(summary)