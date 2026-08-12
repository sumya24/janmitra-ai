"""Pydantic schemas (data validation), distinct from backend/models.py (SQLAlchemy ORM).

Anything here is a shape for data that either isn't persisted in the relational DB at all
(e.g. the RAG knowledge base — see rag_knowledge.py) or is a request/response contract layered
on top of an ORM model. Keeping this separate from models.py mirrors how backend/routes/*.py
already defines its own Pydantic request/response classes rather than reusing ORM classes directly.
"""
