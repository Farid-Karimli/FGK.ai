from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from typing import List
from langchain.schema.document import Document

import os


class RetrieverFile:
       
    def __init__(self, type, filename):
           self.type = type
           self.filename = filename

    def __repr__(self):
        return f"RetrieverFile({self.type}, {self.filename})"

class Retriever:
   
    def __init__(self, type):
       self.files = []
       self.documents = []
       self.type = type
       self.embeddings = OpenAIEmbeddings()
       self.db = None

    def add_file(self, file, type):
         self.files.append(RetrieverFile(type, file))

    def load_text(self, txt_file):
        loader = TextLoader(txt_file)
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=10, chunk_overlap=0
    )
        texts = text_splitter.split_documents(loader.load())
        return texts

    def load_csv(self, csv_file):
        loader = CSVLoader(csv_file)
        return loader.load()
    
    def load_files(self):
        documents: List[Document] = []
        for file in self.files:
              if file.type == "text":
                documents.extend(self.load_text(file.filename))
              else:
                documents.extend(self.load_csv(file.filename))
        self.documents = documents

    def create_vector_store(self):
        self.db = FAISS.from_documents(self.documents, self.embeddings)
        
    def search(self, query):
        return self.db.as_retriever().get_relevant_documents(query)
    
    def get_retriever(self):
        return self.db.as_retriever()
    

def main():
    retriever = Retriever("text")
    retriever.add_file("./data/RAG/personal_data.txt", "text")
    retriever.add_file("./data/RAG/answers.csv", "csv")
    retriever.load_files()
    retriever.create_vector_store()

    result = retriever.db.similarity_search("I am a student at Boston University")
    for d in result:
        print(d.page_content)