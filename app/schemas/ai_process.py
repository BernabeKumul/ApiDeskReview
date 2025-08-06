"""
Schemas for AI Process endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentReference(BaseModel):
    """Document reference within a question."""
    DocumentId: int = Field(..., description="Unique document identifier")
    URL: str = Field(..., description="Document URL or path")


class QuestionDocument(BaseModel):
    """Question with associated documents."""
    QuestionID: int = Field(..., description="Unique question identifier")
    DocumentsId: List[DocumentReference] = Field(..., description="List of documents for this question")


class AuditProcessRequest(BaseModel):
    """Request model for audit processing."""
    AuditID: int = Field(..., description="Unique audit identifier")
    OrgID: int = Field(..., description="Organization identifier")
    Operation: str = Field(..., description="Operation name")
    Products: str = Field(..., description="Products being audited")
    Documents: List[QuestionDocument] = Field(..., description="Questions and associated documents")


class FileSearchResult(BaseModel):
    """File search result."""
    FileName: str = Field(..., description="Name of the file")
    DocumentID: str = Field(..., description="Document identifier")


class AuditProcessResponse(BaseModel):
    """Response model for audit processing."""
    ComplianceLevel: int = Field(default=2, description="Compliance level (always 2)")
    Comments: str = Field(..., description="Detailed compliance comments")
    FilesSearch: List[FileSearchResult] = Field(..., description="List of files searched")


class QuestionResponse(BaseModel):
    """Response model for a single question."""
    ComplianceLevel: int = Field(default=2, description="Compliance level (always 2)")
    Comments: str = Field(..., description="Detailed compliance comments")
    FilesSearch: List[FileSearchResult] = Field(..., description="List of files searched")
    QuestionID: str = Field(..., description="Question identifier")


class MultipleQuestionsResponse(BaseModel):
    """Response model for multiple questions audit processing."""
    success: bool = Field(default=True, description="Whether the processing was successful")
    message: str = Field(..., description="Response message")
    data: List[QuestionResponse] = Field(..., description="List of responses for each question")
    total_questions: int = Field(..., description="Total number of questions processed")