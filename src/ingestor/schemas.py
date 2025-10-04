"""
Pydantic schemas for API request/response validation.
"""
from __future__ import annotations

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    """Request model for ingestion endpoint."""
    
    city: str = Field(default="Bangkok", description="City name")
    latitude: float = Field(default=13.7563, description="Latitude")
    longitude: float = Field(default=100.5018, description="Longitude")
    hour_offset: int = Field(default=0, description="Hour offset from current time")


class IngestionResponse(BaseModel):
    """Response model for ingestion endpoint."""
    
    status: str = Field(description="Ingestion status (success/failure)")
    message: str = Field(description="Human-readable message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional details")


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(description="Service health status")
    service: str = Field(description="Service name")
