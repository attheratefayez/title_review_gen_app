"""
pdf-ingestion pipeline
"""

import json
import tempfile
from pathlib import Path
from langchain_core.documents import Document

import opendataloader_pdf



def _convert_pdf_to_json(pdf_path: str, output_dir: str) -> Path:
    """
    Convert PDF to JSON with reading order enabled.

    Args:
        pdf_path: str
        output_dir: str

    Returns: Path
        Full path of the created json
    """
    opendataloader_pdf.convert(
        input_path=pdf_path,
        output_dir=output_dir,
        format="json",
        reading_order="xycut",
        quiet=True,
    )
    pdf_name = Path(pdf_path).stem
    return Path(output_dir) / f"{pdf_name}.json"


def _load_document(json_path: Path) -> dict:
    """
    Load the JSON output from OpenDataLoader.

    Args:
        json_path: Path

    Returns: dict
    """
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


class ChunkPdf:

    def __init__(self, pdf_path: str | Path):

        pdf_path = pdf_path if isinstance(pdf_path, Path) else Path(pdf_path)

        if not pdf_path.exists():
            raise FileExistsError("File doesn't exits")

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = _convert_pdf_to_json(str(pdf_path), temp_dir)
            self.__doc = _load_document(json_path)

    def chunk_by_element(self) -> list[Document]:
        """
        Strategy 1: Chunk by semantic element.

        Creates one chunk per paragraph, heading, or list element.
        Best for: Fine-grained retrieval, precise citations.
        """
        chunks = []
        for element in self.__doc.get("kids", []):
            if element.get("type") in ("paragraph", "heading", "list"):
                chunks.append(
                    {
                        "text": element.get("content", ""),
                        "metadata": {
                            "type": element["type"],
                            "page": element.get("page number"),
                            "bbox": element.get("bounding box"),
                            "source": self.__doc.get("file name"),
                        },
                    }
                )
        docs = []
        for chunk in chunks:
            docs.append(
                Document(
                    page_content=chunk.get("text", ""),
                    metadata=chunk.get("metadata", {}),
                )
            )

        return docs

    def chunk_by_section(self) -> list[Document]:
        """
        Strategy 2: Chunk by heading/section.

        Groups content under headings into coherent sections.
        Best for: Context-rich retrieval, topic-based search.
        """
        chunks = []
        current_heading = None
        current_content: list[str] = []
        current_start_page = None

        for element in self.__doc.get("kids", []):
            element_type = element.get("type")

            if element_type == "heading":
                # Save previous section
                if current_content:
                    chunks.append(
                        {
                            "text": "\n".join(current_content),
                            "metadata": {
                                "heading": current_heading,
                                "page": current_start_page,
                                "source": self.__doc.get("file name"),
                            },
                        }
                    )
                current_heading = element.get("content", "")
                current_content = [current_heading]
                current_start_page = element.get("page number")
            elif element_type in ("paragraph", "list"):
                content = element.get("content", "")
                if content:
                    current_content.append(content)

        # Save the last section
        if current_content:
            chunks.append(
                {
                    "text": "\n".join(current_content),
                    "metadata": {
                        "heading": current_heading,
                        "page": current_start_page,
                        "source": self.__doc.get("file name"),
                    },
                }
            )

        docs = []
        for chunk in chunks:
            docs.append(
                Document(
                    page_content=chunk.get("text", ""),
                    metadata=chunk.get("metadata", {}),
                )
            )

        return docs

    def chunk_with_min_size(self, min_chars: int = 200) -> list[dict]:
        """
        Strategy 3: Merge adjacent elements until minimum size.

        Combines small paragraphs to avoid overly fragmented chunks.
        Best for: Balanced chunk sizes, reducing noise.
        """
        chunks = []
        buffer_text = ""
        buffer_pages: list[int] = []

        for element in self.__doc.get("kids", []):
            if element.get("type") in ("paragraph", "heading", "list"):
                content = element.get("content", "")
                page = element.get("page number")

                buffer_text += content + "\n"
                if page and page not in buffer_pages:
                    buffer_pages.append(page)

                if len(buffer_text) >= min_chars:
                    chunks.append(
                        {
                            "text": buffer_text.strip(),
                            "metadata": {
                                "pages": buffer_pages.copy(),
                                "source": self.__doc.get("file name"),
                            },
                        }
                    )
                    buffer_text = ""
                    buffer_pages = []

        # Save remaining buffer
        if buffer_text.strip():
            chunks.append(
                {
                    "text": buffer_text.strip(),
                    "metadata": {
                        "pages": buffer_pages,
                        "source": self.__doc.get("file name"),
                    },
                }
            )

        docs = []
        for chunk in chunks:
            docs.append(
                Document(
                    page_content=chunk.get("text", ""),
                    metadata=chunk.get("metadata", {}),
                )
            )

        return docs


if __name__ == "__main__":

    loaded_pdf = ChunkPdf(
        "./assets/dataset/synthetic_data/ARM Mortgage with Rate Adjustments.pdf"
    )
    chunks = loaded_pdf.chunk_by_element()
