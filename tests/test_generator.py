import json
import pytest
import pandas as pd
from pathlib import Path
from reporting import ReportGenerator

@pytest.fixture
def mock_data(tmp_path):
    metrics_path = tmp_path / "metrics.csv"
    answers_path = tmp_path / "answers.csv"
    
    metrics_data = {
        "id": [1, 2, 3],
        "accuracy": [1.0, 0.0, 1.0],
        "latency": [100, 200, 150]
    }
    answers_data = {
        "id": [1, 2, 3],
        "prediction": ["A", "B", "C"],
        "ground_truth": ["A", "A", "C"]
    }
    
    pd.DataFrame(metrics_data).to_csv(metrics_path, index=False)
    pd.DataFrame(answers_data).to_csv(answers_path, index=False)
    
    return metrics_path, answers_path

def test_report_generation(mock_data, tmp_path):
    metrics_path, answers_path = mock_data
    config = {
        "model": {"name": "TestModel"},
        "task": {"name": "TestTask"},
        "dataset": {"path": "/path/to/dataset"}
    }
    output_dir = tmp_path / "output"
    
    # Create template directory and file
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "report.md.j2"
    template_file.write_text("# Report for {{ summary.model_name }}\nAccuracy: {{ summary.metrics.accuracy.mean }}")
    
    generator = ReportGenerator(
        metrics_path=metrics_path,
        answers_path=answers_path,
        config=config,
        output_dir=output_dir,
        template_dir=template_dir
    )
    
    generator.run()
    
    assert (output_dir / "final_report.md").exists()
    assert (output_dir / "report_data.json").exists()
    
    with open(output_dir / "report_data.json") as f:
        data = json.load(f)
        assert data["model_name"] == "TestModel"
        assert data["metrics"]["accuracy"]["mean"] == pytest.approx(0.6666, rel=1e-3)