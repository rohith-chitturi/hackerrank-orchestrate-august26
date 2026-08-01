import os
import sys
import math
from collections import Counter
from typing import List
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.state import RoutingContext
from models.results import RetrievedEvidence

class SimpleBM25:
    """Pure Python BM25 implementation to avoid C-extension compilation issues on Windows."""
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avgdl = sum(len(doc) for doc in corpus) / self.corpus_size if self.corpus_size > 0 else 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        
        df = {}
        for document in corpus:
            self.doc_len.append(len(document))
            frequencies = Counter(document)
            self.doc_freqs.append(frequencies)
            for word in frequencies:
                if word not in df:
                    df[word] = 0
                df[word] += 1

        for word, freq in df.items():
            self.idf[word] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)

    def get_scores(self, query):
        scores = [0.0] * self.corpus_size
        for q in query:
            if q not in self.idf:
                continue
            idf = self.idf[q]
            for i, doc_freq in enumerate(self.doc_freqs):
                if q in doc_freq:
                    tf = doc_freq[q]
                    doc_len = self.doc_len[i]
                    score = idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl))
                    scores[i] += score
        return scores

class RetrievalService:
    def __init__(self, history_df: pd.DataFrame):
        self.user_indices = {}
        self.user_documents = {}
        self.build_index(history_df)
        
    def build_index(self, df: pd.DataFrame):
        # Group historical messages by user_id for user-scoped search
        if df.empty:
            return
            
        for user_id, group in df.groupby("user_id"):
            documents = []
            for _, row in group.iterrows():
                text = str(row.get("message_text", ""))
                msg_id = str(row.get("message_id", ""))
                documents.append({"id": msg_id, "text": text})
                
            self.user_documents[user_id] = documents
            
            tokenized_corpus = [doc["text"].lower().split(" ") for doc in documents]
            if tokenized_corpus:
                self.user_indices[user_id] = SimpleBM25(tokenized_corpus)
                
    def retrieve(self, ctx: RoutingContext, top_k: int = 3) -> List[RetrievedEvidence]:
        if not ctx.message.user_id:
            return []
            
        user_id = ctx.message.user_id
        if user_id not in self.user_indices:
            return []
            
        bm25 = self.user_indices[user_id]
        docs = self.user_documents[user_id]
        
        query_text = ctx.normalized_message.normalized_text if ctx.normalized_message else ""
        if not query_text:
            return []
            
        tokenized_query = query_text.lower().split(" ")
        doc_scores = bm25.get_scores(tokenized_query)
        
        results = []
        for idx in sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_k]:
            if doc_scores[idx] > 0.0:
                doc = docs[idx]
                results.append(RetrievedEvidence(
                    message_id=doc["id"],
                    similarity=float(doc_scores[idx]),
                    retrieval_source="BM25"
                ))
                
        return results
