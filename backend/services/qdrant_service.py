import os
import logging
import numpy as np
from typing import Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("qdrant")

class QdrantCompanyRAG:
    def __init__(self):
        self.enabled = False
        self.client = None
        self.collection_name = "company_profiles"
        self.embedding_dim = 384 # Dimension of standard lightweight models
        self.fallback_db = {} # In-memory key-value dictionary as complete fallback
        
        try:
            # Create in-memory client
            self.client = QdrantClient(path=":memory:")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE)
            )
            self.enabled = True
            logger.info("Qdrant in-memory vector DB initialized successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize Qdrant client: {e}. Falling back to in-memory KV search.")
            self.enabled = False
            
        self.prepopulate_database()

    def get_simple_hash_embedding(self, text: str) -> list:
        """
        Generates a quick pseudo-embedding based on word frequencies.
        This enables full operation without downloading heavy ML models.
        """
        words = text.lower().split()
        vector = np.zeros(self.embedding_dim)
        for i, word in enumerate(words):
            # Simple hash to map words to dimensions
            idx = hash(word) % self.embedding_dim
            vector[idx] += 1
            
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()

    def prepopulate_database(self):
        """
        Pre-populates the vector DB with a set of company profiles.
        """
        companies = {
            "Google": {
                "tech_stack": "C++, Java, Python, Go, TensorFlow, JAX, GCP",
                "funding_status": "Publicly Traded (Alphabet)",
                "domain": "Global Search, Advertising, Cloud, Consumer Hardware, AI Research (DeepMind)",
                "recent_news": "Recently released Gemini 1.5 Pro and Gemini 1.5 Flash models with up to 2 million token context windows."
            },
            "OpenAI": {
                "tech_stack": "Python, PyTorch, Kubernetes, Azure Cloud, Triton",
                "funding_status": "Non-profit/For-profit Hybrid ($13B funding from Microsoft)",
                "domain": "Artificial General Intelligence (AGI) research, ChatGPT, API services",
                "recent_news": "Announced GPT-4o with real-time audio, visual, and text interaction capabilities."
            },
            "Anthropic": {
                "tech_stack": "Python, PyTorch, AWS, GCP, TypeScript",
                "funding_status": "Series C/D ($7.3B raised from Amazon, Google)",
                "domain": "AI Safety and Research, Claude LLM models, API services",
                "recent_news": "Released Claude 3.5 Sonnet, demonstrating top-tier coding and reasoning benchmarks."
            },
            "Microsoft": {
                "tech_stack": "C#, TypeScript, C++, Python, Azure, SQL Server",
                "funding_status": "Publicly Traded",
                "domain": "Enterprise Cloud, Operating Systems, Office Productivity, AI Copilots",
                "recent_news": "Integrating GPT models into Windows, Office 365, and GitHub Copilot."
            },
            "Meta": {
                "tech_stack": "Python, C++, Hack, PyTorch, Llama Models, React",
                "funding_status": "Publicly Traded",
                "domain": "Social Media, Virtual Reality, Open Source AI models (Llama)",
                "recent_news": "Released Llama 3 models, making high-performance open-weights LLMs freely accessible."
            }
        }
        
        for name, profile in companies.items():
            self.add_company_profile(name, profile)

    def add_company_profile(self, name: str, profile: Dict[str, str]):
        """
        Adds a company profile to the vector DB or fallback DB.
        """
        # Save to fallback DB in all cases for simple lookup
        normalized_name = name.strip().lower()
        self.fallback_db[normalized_name] = profile
        
        if self.enabled and self.client:
            try:
                # Combine fields into text for embedding
                text_blob = f"Company: {name}. Tech: {profile.get('tech_stack')}. Funding: {profile.get('funding_status')}. Domain: {profile.get('domain')}. News: {profile.get('recent_news')}"
                vector = self.get_simple_hash_embedding(text_blob)
                
                point_id = hash(normalized_name) % 10000000
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        PointStruct(
                            id=point_id,
                            vector=vector,
                            payload={
                                "name": name,
                                "tech_stack": profile.get("tech_stack"),
                                "funding_status": profile.get("funding_status"),
                                "domain": profile.get("domain"),
                                "recent_news": profile.get("recent_news")
                            }
                        )
                    ]
                )
            except Exception as e:
                logger.error(f"Error adding to Qdrant vector store: {e}")

    def query_company_profile(self, company_name: str) -> Optional[Dict[str, str]]:
        """
        Queries the vector DB for a company profile. If not found, attempts simple keyword matching.
        """
        if not company_name:
            return None
            
        normalized_name = company_name.strip().lower()
        
        # Check direct lookup first (most accurate for exact match)
        if normalized_name in self.fallback_db:
            return self.fallback_db[normalized_name]
            
        # Try soft match using key overlap
        for k, profile in self.fallback_db.items():
            if k in normalized_name or normalized_name in k:
                return profile
                
        # Try Qdrant vector search
        if self.enabled and self.client:
            try:
                vector = self.get_simple_hash_embedding(company_name)
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=vector,
                    limit=1
                )
                if results:
                    best_match = results[0]
                    # Only accept if match score is reasonably high
                    if best_match.score > 0.3:
                        payload = best_match.payload
                        return {
                            "tech_stack": payload.get("tech_stack", "Unknown"),
                            "funding_status": payload.get("funding_status", "Unknown"),
                            "domain": payload.get("domain", "Unknown"),
                            "recent_news": payload.get("recent_news", "Unknown")
                        }
            except Exception as e:
                logger.error(f"Error searching Qdrant: {e}")
                
        # Return fallback details if completely unknown
        return None

# Singleton instance
rag_service = QdrantCompanyRAG()
