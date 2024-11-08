from langchain_community.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from app.core.config import settings
from app.services.s3 import S3Service
import tempfile
import os
import numpy as np
from typing import List

class SimpleVectorStore:
    def __init__(self, documents: List[Document], embeddings):
        self.documents = documents
        self.embeddings = embeddings
        self.doc_embeddings = []
        self._create_embeddings()

    def _create_embeddings(self):
        texts = [doc.page_content for doc in self.documents]
        self.doc_embeddings = self.embeddings.embed_documents(texts)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        query_embedding = self.embeddings.embed_query(query)
        
        # Calculate similarities
        similarities = []
        for doc_embedding in self.doc_embeddings:
            similarity = np.dot(query_embedding, doc_embedding)
            similarities.append(similarity)
        
        # Get top k similar documents
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        return [self.documents[i] for i in top_k_indices]

class RAGService:
    def __init__(self):
        self.s3 = S3Service()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GOOGLE_API_KEY,
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
            convert_system_message_to_human=True
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    async def process_document(self, file_url: str) -> SimpleVectorStore:
        """Process a document and create a vector store"""
        # Download file from S3
        file_key = file_url.split(f"{self.s3.bucket_name}.s3.amazonaws.com/")[1]
        file_data = await self.s3.get_file(file_key)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_data.read())
            temp_path = temp_file.name
        
        try:
            # Load and process document
            loader = PDFPlumberLoader(temp_path)
            documents = loader.load()
            texts = self.text_splitter.split_documents(documents)
            
            # Create simple vector store
            vectorstore = SimpleVectorStore(texts, self.embeddings)
            return vectorstore
            
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    async def query_document(self, vectorstore: SimpleVectorStore, question: str) -> dict:
        """Query a processed document"""
        # Get relevant documents
        relevant_docs = vectorstore.similarity_search(question)
        
        # Combine relevant documents into context
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Create prompt
        prompt = f"""Based on the following context, please answer the question. You can:
1. Directly quote from the context when available
2. Make logical inferences ONLY if they are clearly supported by the context
3. For questions about themes/morals, explain your reasoning using evidence from the text
4. If information isn't in the context, say "I cannot find this information in the document."

Context:
{context}

Question: {question}

Answer:"""
        
        # Get response from LLM
        response = self.llm.invoke(prompt)
        
        return {
            "answer": response.content,
            "source_documents": [doc.page_content[:200] + "..." for doc in relevant_docs]
        } 