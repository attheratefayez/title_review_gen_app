from . import config
from .agent import DraftGenAgent

from .ingestion.pdf_chunking import ChunkPdf

# NOTE: 
#     since the synthetic documents are really small, 
#     retriaval is wokring very poorly. This TestAgent class 
#     chunks the pdf, and feeds the chunks directly into the llms 
#     system_prompt. 
#     We can introduce retrival later with better documents

class TestAgent:

    def __init__(self, file_path: str):
        self.__data = ChunkPdf(file_path).chunk_by_section()
        self.__system_promt = config.SYSTEM_PROMPT.format(
            document="\n".join([doc.page_content for doc in self.__data]),
            source=self.__data[0].metadata.get("source", "")
            + "page"
            + str(self.__data[0].metadata.get("page", "")),
        )

        self.__report = DraftGenAgent().invoke(self.__system_promt).get("messages")[-1].content

    def generate_report(self):
        return self.__report
