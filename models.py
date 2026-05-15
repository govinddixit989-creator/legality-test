from datetime import datetime
from pydantic import BaseModel, field_validator


class NodeCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v


class NodeResponse(BaseModel):
    id: int
    name: str


class EdgeCreate(BaseModel):
    source: str
    destination: str
    latency: float

    @field_validator("latency")
    @classmethod
    def latency_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("latency must be greater than 0")
        return v


class EdgeResponse(BaseModel):
    id: int
    source: str
    destination: str
    latency: float


class RouteRequest(BaseModel):
    source: str
    destination: str


class RouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class HistoryEntry(BaseModel):
    id: int
    source: str
    destination: str
    total_latency: float | None
    path: list[str] | None
    created_at: datetime
