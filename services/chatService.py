from DTO.llmConfig import LLMConfig
from factory.llmFactory import LLMFactory
from interfaces.llmProvider import LLMProvider
from services.pageService import PageService
from services.embeddingService import EmbeddingService


class ChatService:

    #lol maybe put all ts in the constructor. maybe try using builder idk. builder mgiht be too much actuallgy
    #create bothh chatclient and rephraserclient in routes. get config from config which would be something like the .env file for configs. we change our model there itself.
    def get_response(self, chatClient: LLMProvider, rephraserClient: LLMProvider, embeddingClient: EmbeddingService, pageService: PageService, query, messages, config: LLMConfig):

        #call query rephraser
        rephrased_query = rephraserClient.chat(query, [], config)

        #call query embedder
        query_embeddings = embeddingClient.get_embeddings(rephrased_query) #put this in list later if chunks are required to be in a list

        #call vector searcher
        relevant_titles = embeddingClient.get_relevant_chunks(query_embeddings) #add top k here if required, currently set to 5

        #fetch docs from db
        content = pageService.get_document_list(relevant_titles)

        #call llmClient.chat
        #now how to pass ts? get only 2 pages? check how long the pages actually are. 

        pass