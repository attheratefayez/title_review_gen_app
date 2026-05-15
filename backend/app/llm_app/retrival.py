from . import config
from collections import defaultdict
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from nltk import word_tokenize


class HybridRetriever:
    """
    HybridRetriever class.
    Uses BM25 and MMR algorithm to retrive similar docs then uses RRF score to rerank them.
    """

    def __init__(self):
        """Instantiates Hybrid Retriver"""
        self.__embeddings_func = OllamaEmbeddings(model=config.EMBEDDINGS_MODEL)
        self.__vector_db = Chroma(
            collection_name=config.VEC_STORE_COLLECTION_NAME,
            embedding_function=self.__embeddings_func,
            persist_directory=str(config.VEC_STORE_PERSIST_PATH),
        )

        db_rets = self.__vector_db.get(include=["metadata", "documents"])
        all_docs = db_rets.get("documets", [])
        all_ids = db_rets.get("ids", [])

        doc_iters = [
            Document(page_content=doc, metadata={"id": id})
            for doc, id in zip(all_docs, all_ids)
        ]

        self.__bm25_retriever = BM25Retriever.from_documents(
            doc_iters, preprocess_func=word_tokenize, k=5
        )
        self.__mmr_retriever = self.__vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 50, "lambda_mult": 0.25},
        )

    def hybrid_search(self, query: str, k=50):
        """
        Performs BM25 and MMR retrieval with the given query
        and then reranks the resutls using RRF-scoring.

        Args:
            k: int (defaul: 50)
            query: [str]

        Returns:
        results sorted on score
        """
        bm25_rets = self.__bm25_retriever.invoke(query)
        mmr_rets = self.__mmr_retriever.invoke(query)

        scores = defaultdict(float)

        for rank, doc in enumerate(bm25_rets, start=1):
            scores[doc.metadata.get("id")] += 1 / (rank + k)

        for rank, doc in enumerate(mmr_rets, start=1):
            scores[doc.metadata.get("id")] += 1 / (rank + k)

        return sorted(scores, key=lambda x: x[1], reverse=True)
