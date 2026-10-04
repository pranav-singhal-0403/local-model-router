from pathlib import Path
from typing import List

import pymupdf


def parse_pdf(pdf_path: Path) -> List[dict]:
    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    document.close()

    return pages