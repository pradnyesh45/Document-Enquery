from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from app.services.vector_store import VectorStore
from app.core.config import get_settings
from typing import List, Dict
from sqlalchemy.orm import Session
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

class RAGAgent:
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStore(db)
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-4",
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that answers questions based on the provided context. 
            Always base your answers on the context provided and acknowledge when you're unsure about something.
            If the context doesn't contain relevant information, say so."""),
            ("user", """Context: {context}
            
            Question: {question}
            
            Please provide a detailed answer based on the context above.""")
        ])
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    async def _format_context(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks into a single context string"""
        return "\n\n".join([chunk["content"] for chunk in chunks])
    
    async def answer_question(
        self, 
        question: str, 
        document_ids: List[UUID]
    ) -> Dict:
        """Answer a question using RAG"""
        try:
            # Get relevant chunks using similarity search
            relevant_chunks = await self.vector_store.similarity_search(
                query=question,
                document_ids=document_ids,
                limit=3
            )

            # Format context from chunks
            context = "\n\n".join([chunk["content"] for chunk in relevant_chunks])

            # Generate response using LLM
            response = await self.llm.generate_response(question, context)

            return {
                "answer": response,
                "sources": relevant_chunks
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise Exception(f"Failed to generate answer: {str(e)}") 