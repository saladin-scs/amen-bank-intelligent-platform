# Amen Bank AI Engine

Independent CRISP-DM AI project for the Amen Bank Intelligent Digital Banking Platform.

The AI Engine is **not** part of the FastAPI backend. Backend AI service only consumes artifacts produced here.

## Status

| CRISP-DM phase | Status |
| --- | --- |
| Business Understanding | Planned (notebooks) |
| Data Understanding | Planned (notebooks) |
| Data Preparation | **Completed** — see `datasets/` |
| Modeling / Embeddings | Next |
| Evaluation | Dataset ready (`datasets/evaluation/`) |
| Deployment | Pending |

## Knowledge base

```bash
cd preprocessing
pip install -r requirements.txt
python run_pipeline.py
pytest test_pipeline.py
```

Documentation: [`datasets/README.md`](datasets/README.md)
