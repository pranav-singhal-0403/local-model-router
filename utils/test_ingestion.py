from pathlib import Path
from backend.ingestion_pipeline import IngestionPipeline


pdf_path = Path(r"C:\Users\prana\OneDrive\Documents\GitHub\local-model-router\data\documents\Pranav_Singhal_Resume.pdf")

pipeline = IngestionPipeline()

result = pipeline.ingest_pdf(pdf_path)

print(result)