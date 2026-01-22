# Reporting Engine

[Русский](README.ru.md)

Reporting engine for VLMHyperBench. Generates Markdown and JSON reports from evaluation results.

## Data Flow

```mermaid
graph LR
    A[Metrics CSV] --> C[ReportGenerator]
    B[Answers CSV] --> C
    D[Config YAML] --> C
    C --> E[final_report.md]
    C --> F[report_data.json]
```

## Installation

```bash
pip install -e .
```

## Usage

```python
from reporting import ReportGenerator