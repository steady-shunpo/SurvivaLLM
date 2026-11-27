from repository.pagesRepository import PagesRepository


class PageService:

    def __init__(self, repository):
        self.repository = repository

    def create_document(self, title, content):
        #clean doc here????
        self.repository.createDocument({
            "title": title,
            "content": content
        })
    
    def get_document_list(self, titles):
        content = self.repository.fetchDocuments(titles)
        return content
