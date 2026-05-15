import config

from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from .pdf_chunking import ChunkPdf

from paddleocr import PaddleOCR

class PaddleTextExtractor:
    """
    Extract all text from images or PDFs using PaddleOCR.
    """

    def __init__(
        self,
        lang="en",
        use_angle_cls=True,
        show_log=False,
    ):
        self.ocr = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang=lang,
            show_log=show_log,
        )

    # HACK: have to improve it later
    # for now its writing the retrieved text in a pdf, 
    # so that ingestion pipeline can read the pdf and stays happy
    def _write_pdf(self, content: str):

        with open("/tmp/extracted_image.pdf", "wb") as file:
            file.write(content.encode("utf-8"))

        return "/tmp/extracted_image.pdf"

    def extract_from_image(self, image_path):
        """
        Extract text from an image file.

        Returns:
            str: extracted text
        """
        result = self.ocr.ocr(image_path, cls=True)

        texts = []

        for line in result:
            if line is None:
                continue

            for item in line:
                text = item[1][0]
                texts.append(text)

        full_content = "\n".join(texts)

        file_path = self._write_pdf(full_content)
        return file_path



class IngestionPipeline:
    """
    Document ingestion pipeline.
    From file_loading to indexind and saving in the vector database,
    full pipeline is orchestrated here, like a builder pattern.
    """

    def __init__(self, path: str | Path):
        """
        Create a new IngestionPipeline with a new file.

        Args:
            path: file path to load

        Returns:
        """
        # TODO:
        # - stop indexing already indexed content
        # - if path is a directory, ingest everything (images, pdfs)??
        # - maybe make the pipeine more robust by letting user pass in different loaders/text_splitters!!

        # to prevent indexing a file more than once
        self.__indexed = False
        self.__path = path if isinstance(path, Path) else Path(path)

        self.__loader = ChunkPdf(self.__path)
        self.__text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600, chunk_overlap=80, add_start_index=True
        )
        self.__embedding_func = OllamaEmbeddings(model=config.EMBEDDINGS_MODEL)

        self.__vec_db = Chroma(
            collection_name=config.VEC_STORE_COLLECTION_NAME,
            embedding_function=self.__embedding_func,
            persist_directory=str(config.VEC_STORE_PERSIST_PATH),
        )

    def _read_and_chunk(self):
        """Read the file, if exists, create chunks, and return them as Documents.

        Returns:
        """
        self.__docs = self.__loader.chunk_by_section()
        return self

    def _split_documents(self):
        """Using the text_splitter, split the documents for better ingestion.

        Returns:
        """
        self.__docs = self.__text_splitter.split_documents(self.__docs)
        return self

    def _index_documents(self):
        """Generate embeddings for the documents, and save the embeddings in a Chromadb.

        Returns:
        """
        self.__id = self.__vec_db.add_documents(self.__docs)
        self.__indexed = bool(self.__id)

        return self

    def ingest(self):
        """Run the full ingestion-pipeline on a file, and save the embeddings.

        Returns:
            [TODO:return]
        """
        if not self.__indexed:
            self._read_and_chunk()\
            ._split_documents()\
            ._index_documents()

        return self.__id
