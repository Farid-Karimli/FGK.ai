from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter

from rag import Retriever

class Model:

    def __init__(self, model_name):
        self.model = ChatOpenAI(model=model_name)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You imitate the way I talk. Your name is FGK, you're a Data Science graduate student at BU."),
            #MessagesPlaceholder(variable_name="history"),
            ("user", "{input}")
        ])
        self.memory = ConversationBufferMemory(return_messages=True)

        retriever_ = Retriever("vector")
        retriever_.add_file("./data/RAG/personal_data.txt", "text")
        retriever_.add_file("./data/RAG/answers.csv", "csv")
        retriever_.load_files()
        retriever_.create_vector_store()

        retriever = retriever_.get_retriever()

        self.chain = (  \
            {"context": retriever, "input": RunnablePassthrough()} \
            | self.prompt | self.model | StrOutputParser()
        ) # RunnablePassthrough.assign(history=RunnableLambda(self.memory.load_memory_variables) | itemgetter("history"))

    def get_chain(self):
        return self.chain
    

def main():
    model = Model("ft:gpt-3.5-turbo-1106:boston-university::8kkN3yKE")
    chain = model.get_chain()

    inputs = "What are your likes?"
    response = chain.invoke(inputs)
    print(response)





    