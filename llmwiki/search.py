from rank_bm25 import BM25Okapi

class WikiSearch:
    def __init__(self, wiki_path="wiki"):
        self.wiki_path = Path(wiki_path)
        self._index_wiki()

    def _index_wiki(self):
        self.files = list(self.wiki_path.glob("*.md"))
        self.corpus = [f.read_text().split() for f in self.files]
        self.bm25 = BM25Okapi(self.corpus)

    def query(self, question, k=3):
        tokenized_query = question.split()
        top_docs = self.bm25.get_top_n(tokenized_query, self.files, n=k)
        # Final answer is synthesized from these retrieved pages [4, 5]
        return assemble_and_answer(top_docs, question)
