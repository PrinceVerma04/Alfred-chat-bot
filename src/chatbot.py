"""LangChain chatbot implementation for Alfred Lab."""

import logging
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage

from src.config import (
    COMPANY_NAME,
    CONVERSATION_HISTORY_SIZE,
    CONTACT_EMAIL,
    CONTACT_HOURS,
    CONTACT_PHONE,
    GROQ_API_KEY,
    GROQ_MODEL_NAME,
    LLM_PROVIDER,
    MODEL_NAME,
    OPENAI_API_KEY,
)
from src.vector_store import load_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Custom prompt template for company chatbot
CUSTOM_PROMPT = """You are a helpful AI assistant for {company_name}.
Answer only from the provided website context. If the context does not contain the answer,
say that you do not have enough information from the company website.
Keep answers concise, friendly, and useful.

Official contact information:
- Phone: {contact_phone}
- Email: {contact_email}
- Phone reception hours: {contact_hours}

If users ask how to contact Alfred Lab, book a session, call, email, or make an inquiry,
provide the official contact information above and mention they can use the one-on-one
session form in the web interface.

Website context:
{context}

Question: {question}

Answer:"""


class AlfredChatbot:
    """LangChain-powered chatbot for Alfred Lab."""
    
    def __init__(self):
        self.llm = self._create_llm()
        self.vector_store = None
        self.chat_history = ChatMessageHistory()
        self._initialize_chain()

    def _create_llm(self):
        """Create the configured chat model."""
        if LLM_PROVIDER == "groq":
            if not GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is missing. Add your gsk_ key to .env or set LLM_PROVIDER=openai.")
            return ChatOpenAI(
                model=GROQ_MODEL_NAME,
                temperature=0.2,
                openai_api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )

        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            raise ValueError("OPENAI_API_KEY is missing. Add it to .env or set LLM_PROVIDER=groq.")
        return ChatOpenAI(
            model=MODEL_NAME,
            temperature=0.2,
            openai_api_key=OPENAI_API_KEY,
        )
    
    def _initialize_chain(self):
        """Load the FAISS vector store."""
        self.vector_store = load_vector_store()
        
        if self.vector_store:
            logger.info("Chatbot initialized with vector store")
        else:
            logger.warning("No vector store found. Please run with --scrape first.")
    
    def chat(self, user_input: str) -> dict:
        """
        Process user input and return chatbot response.
        
        Args:
            user_input: User's question or message.
            
        Returns:
            Dictionary with answer and source documents.
        """
        if not self.vector_store:
            return {
                "answer": "Chatbot not initialized. Please run `python main.py --scrape` first to load company data.",
                "sources": []
            }
        
        try:
            source_documents = self.vector_store.similarity_search(user_input, k=4)
            context = "\n\n---\n\n".join(doc.page_content for doc in source_documents)
            prompt = CUSTOM_PROMPT.format(
                company_name=COMPANY_NAME,
                contact_phone=CONTACT_PHONE,
                contact_email=CONTACT_EMAIL,
                contact_hours=CONTACT_HOURS,
                context=context,
                question=user_input,
            )

            ai_message = self.llm.invoke(prompt)
            answer = ai_message.content
            
            # Add to chat history
            self.chat_history.add_user_message(user_input)
            self.chat_history.add_ai_message(answer)
            
            # Trim history if too long
            if len(self.chat_history.messages) > CONVERSATION_HISTORY_SIZE * 2:
                self.chat_history.messages = self.chat_history.messages[-(CONVERSATION_HISTORY_SIZE * 2):]
            
            # Extract source documents
            sources = []
            for doc in source_documents:
                sources.append({
                    "content": doc.page_content[:200] + ("..." if len(doc.page_content) > 200 else ""),
                    "metadata": doc.metadata,
                })
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "sources": []
            }
    
    def get_chat_history(self) -> list:
        """Get conversation history."""
        return [
            {"role": "user" if isinstance(m, HumanMessage) else "ai", "content": m.content}
            for m in self.chat_history.messages
        ]

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.chat_history.clear()


def create_chatbot() -> AlfredChatbot:
    """
    Factory function to create chatbot instance.
    
    Returns:
        AlfredChatbot instance.
    """
    return AlfredChatbot()


if __name__ == "__main__":
    # Test the chatbot
    print("Initializing Alfred Lab Chatbot...")
    bot = create_chatbot()
    
    # Test question
    test_question = "What does Alfred Lab do?"
    print(f"\nUser: {test_question}")
    
    response = bot.chat(test_question)
    print(f"\nAI: {response['answer']}")
    print(f"\nSources: {len(response['sources'])} documents found")
