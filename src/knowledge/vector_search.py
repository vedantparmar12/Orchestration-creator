from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
from supabase import create_client, Client
import openai
import numpy as np
from pathlib import Path
import json
import os
from datetime import datetime

class Document(BaseModel):
    """Document model for vector storage"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: datetime

class SearchResult(BaseModel):
    """Search result model"""
    document: Document
    similarity_score: float
    rank: int

class VectorKnowledgeBase:
    """Semantic search over documentation and examples using Supabase"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.client: Client = create_client(supabase_url, supabase_key)
        self.openai_client = openai.OpenAI()
        self.embedding_model = "text-embedding-3-small"
        self.table_name = "documents"
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure the documents table exists with proper schema"""
        try:
            # Check if table exists by trying to select from it
            response = self.client.table(self.table_name).select("id").limit(1).execute()
        except Exception as e:
            print(f"Documents table may not exist or have incorrect schema: {e}")
            print("Please ensure your Supabase database has the correct schema.")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    async def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the knowledge base"""
        if metadata is None:
            metadata = {}
        
        # Generate embedding
        embedding = await self.generate_embedding(content)
        
        # Create document
        doc_id = f"doc_{datetime.now().timestamp()}"
        document = {
            "id": doc_id,
            "content": content,
            "metadata": metadata,
            "embedding": embedding,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            response = self.client.table(self.table_name).insert(document).execute()
            return doc_id
        except Exception as e:
            print(f"Error adding document: {e}")
            return ""
    
    async def search_documents(
        self, 
        query: str, 
        limit: int = 5, 
        threshold: float = 0.7,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Build the query
            query_builder = self.client.table(self.table_name).select("*")
            
            # Apply metadata filters if provided
            if metadata_filter:
                for key, value in metadata_filter.items():
                    query_builder = query_builder.eq(f"metadata->{key}", value)
            
            # Execute query
            response = query_builder.execute()
            
            if not response.data:
                return []
            
            # Calculate similarities
            results = []
            for doc_data in response.data:
                if doc_data.get("embedding"):
                    similarity = self._calculate_similarity(query_embedding, doc_data["embedding"])
                    
                    if similarity >= threshold:
                        document = Document(
                            id=doc_data["id"],
                            content=doc_data["content"],
                            metadata=doc_data["metadata"],
                            embedding=doc_data["embedding"],
                            created_at=datetime.fromisoformat(doc_data["created_at"]),
                            updated_at=datetime.fromisoformat(doc_data["updated_at"])
                        )
                        
                        results.append(SearchResult(
                            document=document,
                            similarity_score=similarity,
                            rank=0  # Will be set after sorting
                        ))
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            results = results[:limit]
            
            # Set ranks
            for i, result in enumerate(results):
                result.rank = i + 1
            
            return results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    async def index_project_knowledge(self, docs_path: str, file_patterns: List[str] = None):
        """Index project documentation and examples"""
        if file_patterns is None:
            file_patterns = ["*.md", "*.py", "*.txt", "*.rst"]
        
        docs_path = Path(docs_path)
        if not docs_path.exists():
            print(f"Documentation path does not exist: {docs_path}")
            return
        
        indexed_count = 0
        
        for pattern in file_patterns:
            for file_path in docs_path.rglob(pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Skip empty files
                    if not content.strip():
                        continue
                    
                    # Create metadata
                    metadata = {
                        "file_path": str(file_path),
                        "file_type": file_path.suffix,
                        "file_size": file_path.stat().st_size,
                        "indexed_at": datetime.now().isoformat()
                    }
                    
                    # Add document
                    doc_id = await self.add_document(content, metadata)
                    if doc_id:
                        indexed_count += 1
                        print(f"Indexed: {file_path}")
                
                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")
        
        print(f"Successfully indexed {indexed_count} documents")
    
    async def search_by_category(self, query: str, category: str, limit: int = 5) -> List[SearchResult]:
        """Search documents by category"""
        metadata_filter = {"category": category}
        return await self.search_documents(query, limit, metadata_filter=metadata_filter)
    
    async def get_document_by_id(self, doc_id: str) -> Optional[Document]:
        """Get a specific document by ID"""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", doc_id).execute()
            
            if response.data:
                doc_data = response.data[0]
                return Document(
                    id=doc_data["id"],
                    content=doc_data["content"],
                    metadata=doc_data["metadata"],
                    embedding=doc_data["embedding"],
                    created_at=datetime.fromisoformat(doc_data["created_at"]),
                    updated_at=datetime.fromisoformat(doc_data["updated_at"])
                )
            return None
            
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    async def update_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Update an existing document"""
        try:
            # Generate new embedding
            embedding = await self.generate_embedding(content)
            
            update_data = {
                "content": content,
                "embedding": embedding,
                "updated_at": datetime.now().isoformat()
            }
            
            if metadata:
                update_data["metadata"] = metadata
            
            response = self.client.table(self.table_name).update(update_data).eq("id", doc_id).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        try:
            response = self.client.table(self.table_name).delete().eq("id", doc_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    async def get_similar_documents(self, doc_id: str, limit: int = 5) -> List[SearchResult]:
        """Find documents similar to a given document"""
        document = await self.get_document_by_id(doc_id)
        if not document:
            return []
        
        return await self.search_documents(document.content, limit)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            response = self.client.table(self.table_name).select("id, metadata").execute()
            
            total_docs = len(response.data)
            
            # Count by file type
            file_types = {}
            for doc in response.data:
                file_type = doc["metadata"].get("file_type", "unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                "total_documents": total_docs,
                "file_types": file_types,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    async def clear_knowledge_base(self) -> bool:
        """Clear all documents from the knowledge base"""
        try:
            response = self.client.table(self.table_name).delete().neq("id", "").execute()
            return True
        except Exception as e:
            print(f"Error clearing knowledge base: {e}")
            return False

class KnowledgeManager:
    """High-level knowledge management interface"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.vector_kb = VectorKnowledgeBase(supabase_url, supabase_key)
        self.context_cache = {}
    
    async def get_context_for_query(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for a query"""
        # Check cache first
        if query in self.context_cache:
            return self.context_cache[query]
        
        # Search for relevant documents
        results = await self.vector_kb.search_documents(query, limit=3)
        
        # Combine content from top results
        context_parts = []
        current_length = 0
        
        for result in results:
            content = result.document.content
            if current_length + len(content) <= max_context_length:
                context_parts.append(content)
                current_length += len(content)
            else:
                # Truncate the content to fit
                remaining_length = max_context_length - current_length
                context_parts.append(content[:remaining_length])
                break
        
        context = "\n\n".join(context_parts)
        
        # Cache the result
        self.context_cache[query] = context
        
        return context
    
    async def add_example(self, example_code: str, description: str, tags: List[str] = None):
        """Add a code example to the knowledge base"""
        if tags is None:
            tags = []
        
        metadata = {
            "type": "example",
            "description": description,
            "tags": tags,
            "category": "code_examples"
        }
        
        return await self.vector_kb.add_document(example_code, metadata)
    
    async def search_examples(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Search for code examples"""
        metadata_filter = {"type": "example"}
        return await self.vector_kb.search_documents(query, limit, metadata_filter=metadata_filter)
    
    async def get_examples_by_tags(self, tags: List[str]) -> List[SearchResult]:
        """Get examples by tags"""
        # This would need more complex filtering - simplified for now
        results = []
        for tag in tags:
            tag_results = await self.vector_kb.search_documents(tag, limit=3)
            results.extend(tag_results)
        
        # Remove duplicates and sort by similarity
        seen_ids = set()
        unique_results = []
        for result in results:
            if result.document.id not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result.document.id)
        
        unique_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return unique_results[:5]
