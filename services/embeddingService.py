class EmbeddingService:

    def __init__(self, repository, model):
        self.repository = repository
        self.model = model

    def get_embeddings(self, chunks):
        embeddings = self.model.encode(chunks)
        return embeddings

    def add_embeddings(self, chunks: list, embeddings: list):
        self.repository.add(chunks, embeddings)

    #define top_k later
    def get_relevant_chunks(self, query_embedding, top_k=5):
        relevant_chunks = self.repository.search(query_embedding, top_k)
        return relevant_chunks

    def get_chunks(self, text):
        #chunk text into chunks
        #maybe make this a separate service later if chunking methods differ or if i decide to chunk the docs themselves later
        pass