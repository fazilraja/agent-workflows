"""
docs: https://ai.pydantic.dev/examples/rag/
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, List

import nest_asyncio
import pymongo
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

# Apply nest_asyncio to fix event loop issues in notebooks/interactive environments
nest_asyncio.apply()

# --------------------------------------------------------------
# Define the database connection and dependencies
# --------------------------------------------------------------

@dataclass
class DatabaseDeps:
    """Dependencies for the knowledge base agent."""
    db_conn: DatabaseConn


class DatabaseConn:
    """MongoDB database connection."""
    def __init__(self, uri: str = os.getenv("MONGODB_URI")):
        if not uri:
            raise ValueError("MONGODB_URI environment variable is required")
        self.client = pymongo.MongoClient(uri)
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        self.db = self.client['ai-workflow']
        self.collection = self.db['kb']

    def search_kb(self, query: str) -> List[dict[str, Any]]:
        """Search the knowledge base using regex for both question and answer fields."""
        results = self.collection.find({
            "$or": [
                {"question": {"$regex": query, "$options": "i"}},
                {"answer": {"$regex": query, "$options": "i"}}
            ]
        })
        
        # Convert MongoDB documents to serializable format
        serializable_results = []
        for doc in results:
            serializable_results.append({
                "id": doc["id"],
                "question": doc["question"],
                "answer": doc["answer"]
            })
        
        print(f"Search query: {query}")
        print(f"Found {len(serializable_results)} results")
        return serializable_results

# --------------------------------------------------------------
# Define the structured response model
# --------------------------------------------------------------

class KBResponse(BaseModel):
    """Structured response from the knowledge base agent."""
    answer: str = Field(description="The answer to the user's question from the knowledge base.")
    source: int = Field(description="The ID of the knowledge base entry that provided the answer.")

# --------------------------------------------------------------
# Create the agent with the search tool
# --------------------------------------------------------------

kb_agent = Agent(
    'gpt-4o-mini',
    system_prompt=(
        "You are a helpful assistant that answers questions from the knowledge base about our e-commerce store. "
        "IMPORTANT: Only make ONE search attempt using the search_kb tool. "
        "If the search returns no results, immediately respond with 'I apologize, but I don't have any information about that in my knowledge base.' "
        "and set the source to 0. Do not make multiple search attempts."
    ),
    deps_type=DatabaseDeps,
    result_type=KBResponse,
)


@kb_agent.tool
def search_kb(ctx: RunContext[DatabaseDeps], question: str) -> List[dict[str, Any]]:
    """Search the knowledge base for relevant information."""
    # ctx is the context of the run, it contains the dependencies and the question
    return ctx.deps.db_conn.search_kb(question)

# --------------------------------------------------------------
# Example usage
# --------------------------------------------------------------

db_conn = DatabaseConn()
deps = DatabaseDeps(db_conn=db_conn)

# Example queries
questions = [
    "What is the return policy?",
    "What is the weather in Tokyo?",  # Should indicate no KB info available
]

for question in questions:
    print(f"\nQuestion: {question}")
    result = kb_agent.run_sync(question, deps=deps)
    print(f"Answer: {result.data.answer}")
    print(f"Source: {result.data.source}")
    print("Message History:", result.all_messages())



        
    