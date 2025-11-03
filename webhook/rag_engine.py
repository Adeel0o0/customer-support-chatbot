import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RAGEngine:
    """
    RAG (Retrieval-Augmented Generation) engine for knowledge base search.
    
    Implements:
    - Document loading and chunking
    - Vector embeddings for semantic search
    - LLM-powered answer generation with source attribution
    """
    
    def __init__(self, knowledge_base_path="knowledge_base", persist_directory="./chroma_db"):
        """
        Initialize RAG engine.
        
        Args:
            knowledge_base_path: Path to markdown documents
            persist_directory: Where to store vector embeddings
        """
        self.knowledge_base_path = knowledge_base_path
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.qa_chain = None
        
        # Initialize components
        self._load_documents()
        self._create_vectorstore()
        self._create_qa_chain()
    
    def _load_documents(self):
        """
        Load markdown documents from knowledge base.
        
        LLMOps Practice: Document versioning and tracking
        """
        print(f"Loading documents from {self.knowledge_base_path}...")
        
        # Load all markdown files
        loader = DirectoryLoader(
            self.knowledge_base_path,
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
        
        print(f"Loaded {len(documents)} documents")
        
        # Split documents into chunks
        # Software Engineering: Configurable chunk size for optimization
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Adjust based on content
            chunk_overlap=200,  # Maintain context between chunks
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.chunks = text_splitter.split_documents(documents)
        print(f"Split into {len(self.chunks)} chunks")
    
    def _create_vectorstore(self):
        """
        Create vector store with embeddings.
        
        LLMOps Practice: Embeddings model versioning
        """
        print("Creating vector embeddings...")
        
        # Use OpenAI embeddings
        # LLMOps: Track embedding model version for reproducibility
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # Cost-effective, good quality
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create Chroma vector store
        # Software Engineering: Persistent storage for faster restarts
        self.vectorstore = Chroma.from_documents(
            documents=self.chunks,
            embedding=embeddings,
            persist_directory=self.persist_directory
        )
        
        print(f"Vector store created with {len(self.chunks)} embeddings")
    
    def _create_qa_chain(self):
        """
        Create QA chain with custom prompt using LCEL (LangChain Expression Language).

        LLMOps Practice: Prompt versioning and A/B testing capability
        """
        # Custom prompt template
        # Software Engineering: Prompt as code, version controlled
        prompt_template = """You are a helpful customer support assistant for a SaaS API platform.

Use the following context from our documentation to answer the question. If you cannot find the answer in the context, say "I don't have that information in our documentation. Let me connect you with a human agent."

Always cite which document you got the information from.

Context:
{context}

Question: {question}

Helpful Answer (include source document):"""

        prompt = ChatPromptTemplate.from_template(prompt_template)

        # Initialize LLM
        # LLMOps: Model version tracking, temperature settings
        llm = ChatOpenAI(
            model_name="gpt-4o-mini",  # Cost-effective for support queries
            temperature=0.3,  # Lower = more factual, less creative
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 3}  # Return top 3 most relevant chunks
        )

        # Create LCEL chain: retriever -> format context -> LLM -> parse output
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.qa_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        print("QA chain initialized")
    
    def search(self, query, user_email=None):
        """
        Search knowledge base and generate answer.

        Args:
            query: User's question
            user_email: Optional user context

        Returns:
            dict with answer and sources

        LLMOps Practice: Query logging for model improvement
        """
        print(f"\n--- RAG Search ---")
        print(f"Query: {query}")

        # Execute search - LCEL chain returns the answer directly
        answer = self.qa_chain.invoke(query)

        # Get source documents separately for citation
        source_docs = self.retriever.invoke(query)

        # Extract unique source files
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in source_docs]))

        # Format response
        response = {
            "answer": answer,
            "sources": sources,
            "num_sources": len(source_docs)
        }

        print(f"Answer generated from {len(source_docs)} sources")
        print(f"--- End RAG Search ---\n")

        # LLMOps: Log this query for monitoring and improvement
        # In production: log to database or monitoring service
        self._log_query(query, answer, sources)

        return response
    
    def _log_query(self, query, answer, sources):
        """
        Log queries for LLMOps monitoring.
        
        Software Engineering: Structured logging
        """
        # In production: send to logging service (CloudWatch, Datadog, etc.)
        # For now: simple print for demonstration
        log_entry = {
            "query": query,
            "answer_length": len(answer),
            "num_sources": len(sources),
            "sources": sources
        }
        # print(f"[LOG] {log_entry}")

# Initialize RAG engine (singleton pattern for efficiency)
# Software Engineering: Lazy loading, reuse across requests
_rag_engine_instance = None

def get_rag_engine():
    """
    Get or create RAG engine instance.
    
    Software Engineering: Singleton pattern for resource efficiency
    """
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance

# Example usage
if __name__ == "__main__":
    # Test the RAG engine
    rag = get_rag_engine()
    
    test_queries = [
        "How do I connect Slack?",
        "What's my API rate limit?",
        "How do I cancel my subscription?",
        "Tell me about webhook setup"
    ]
    
    for query in test_queries:
        result = rag.search(query)
        print(f"\nQ: {query}")
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print("-" * 80)