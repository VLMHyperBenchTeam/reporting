# Reporting Engine (Движок отчетов)

[English](README.md)

Модуль генерации отчетов для VLMHyperBench. Создает отчеты в форматах Markdown и JSON на основе результатов оценки.

## Поток данных (Data Flow)

```mermaid
graph LR
    A[Metrics CSV] --> C[ReportGenerator]
    B[Answers CSV] --> C
    D[Config YAML] --> C
    C --> E[final_report.md]
    C --> F[report_data.json]
```

## Установка

```bash
pip install -e .
```

## Использование

```python
from reporting import ReportGenerator