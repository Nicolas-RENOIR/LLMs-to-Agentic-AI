from langchain_community.document_loaders import TextLoader
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
import os
from dotenv import load_dotenv
load_dotenv()

class RAGTool:
    """
    A Retrieval-Augmented Generation (RAG) tool that uses text documents to enhance AI responses
    by incorporating relevant context from a local directory.
    """

    def __init__(self, db_path: str = "/app/src/context"):
        """
        Initializes the RAGTool by setting the API key and context directory.

        Args:
            db_path (str): Path to the directory containing .txt files used for context.
        """
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.db_path = db_path

    def load_context(self):
        """
        Loads all `.txt` files from the context directory into a list of documents.

        Returns:
            list: A list of LangChain document objects loaded from the text files.
        """
        docs = []
        for file_path in os.listdir(self.db_path):
            if file_path.endswith(".txt"):
                loader = TextLoader(os.path.join(self.db_path, file_path))
                docs.extend(loader.load())
        return docs

    def format_context(self, docs):
        """
        Splits documents into chunks, generates embeddings, and creates a retriever for similarity search.

        Args:
            docs (list): A list of documents to process.

        Returns:
            retriever: A FAISS retriever that allows searching for relevant context passages.
        """
        text_splitter = RecursiveCharacterTextSplitter()
        documents = text_splitter.split_documents(docs)
        embeddings = MistralAIEmbeddings(model="mistral-embed", mistral_api_key=self.api_key)
        vector = FAISS.from_documents(documents, embeddings)
        retriever = vector.as_retriever()

        return retriever

    def run(self, usr_prompt):
        """
        Executes the RAG pipeline: loads documents, builds retriever, prompts the model, and returns a response.

        The prompt instructs the model to generate creative advertising prompts and social media descriptions
        based on retrieved context. It outputs JSON responses describing each publication.

        Args:
            usr_prompt (str): The user query or task to process with the help of retrieved context.

        Returns:
            str: The generated JSON-formatted response from the AI model.
        """
        context = self.load_context()
        retriever = self.format_context(context)
        model = ChatMistralAI(mistral_api_key=self.api_key, model="mistral-large-latest")
        prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:
        <context>
        {context}
        </context>
        I already have an image of the product that I will use for each publication.

        Instructions for each publication:

        I want you to give me an english prompt that will use the product image to create an advertising poster highlighting the product and following the company's graphic guidelines.
        For one of the publications, you have to include a human model and describe the scene as if you were a professional photographer, using precise vocabulary.
        For all other publications, specify the angle of view and describe the poster as if you were a designer, using technical vocabulary to make it attractive.

        You'll also need to write a description in english for each publication. They must be catchy, adapted to social networks, with an engaging and creative tone. You can use emojis, ask questions, or appeal to emotion or rarity.

        For each publication, I want you to return only a JSON structure in the following format:

        {{
        ‘date_debut": campaign start date,
        ‘campaign_length": 7,
        ‘prompt": “[prompt to generate a simple poster from the product image]”,
        ‘description": ’[post text to generate engagement on social networks]’
        }}

        Don't give any comments or explanations, make sure you have one JSON objects, each publication, and make sure that the prompts don't ask for any text.
        Question: {input}""")
        document_chain = create_stuff_documents_chain(model, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        response = retrieval_chain.invoke({"input": usr_prompt})
        print("ANSWER", response["answer"][-30:])
        return response["answer"]
