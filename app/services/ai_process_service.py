"""
AI Process Service - Handles audit processing logic.
"""
from typing import List, Dict, Any
from app.schemas.ai_process import AuditProcessRequest, AuditProcessResponse, FileSearchResult
from app.services.ai_service import ai_service
from app.utils.logger import logger


class AIProcessService:
    """
    Service for processing audit information and generating compliance reports.
    """
    
    def __init__(self):
        self.ai_service = ai_service
    
    async def process_audit(self, request: AuditProcessRequest) -> List[Dict[str, Any]]:
        """
        Process audit information and generate compliance response for multiple QuestionIDs.
        
        Args:
            request: Audit process request containing audit details and documents
            
        Returns:
            List[Dict[str, Any]]: List of compliance responses, one for each QuestionID
        """
        try:
            logger.info(f"Processing audit for AuditID: {request.AuditID}, OrgID: {request.OrgID}")
            
            # Extract QuestionIDs from the request
            question_ids = self._extract_question_ids(request.Documents)
            logger.info(f"Found {len(question_ids)} unique QuestionIDs: {question_ids}")
            
            # Prepare documents for AI processing
            documents = self._prepare_documents(request.Documents)
            
            # Process multiple questions using AI service
            ai_responses = await self.ai_service.process_multiple_questions(
                operation=request.Operation,
                products=request.Products,
                question_ids=[str(qid) for qid in question_ids],
                documents=documents
            )
            
            logger.info(f"Audit processing completed for AuditID: {request.AuditID} with {len(ai_responses)} responses")
            return ai_responses
            
        except Exception as e:
            logger.error(f"Error processing audit {request.AuditID}: {e}")
            # Return a default error response for all questions
            question_ids = self._extract_question_ids(request.Documents)
            error_responses = []
            for qid in question_ids:
                error_responses.append({
                    "ComplianceLevel": 2,
                    "Comments": f"Error processing audit: {str(e)}. Unable to complete compliance assessment.",
                    "FilesSearch": [],
                    "QuestionID": str(qid)
                })
            return error_responses if error_responses else [{
                "ComplianceLevel": 2,
                "Comments": f"Error processing audit: {str(e)}. Unable to complete compliance assessment.",
                "FilesSearch": [],
                "QuestionID": "unknown"
            }]
    
    async def process_audit_legacy(self, request: AuditProcessRequest) -> AuditProcessResponse:
        """
        Process audit information and generate compliance response (legacy single response format).
        
        Args:
            request: Audit process request containing audit details and documents
            
        Returns:
            AuditProcessResponse: Compliance response with level, comments, and files
        """
        try:
            logger.info(f"Processing legacy audit for AuditID: {request.AuditID}, OrgID: {request.OrgID}")
            
            # Prepare documents for AI processing
            documents = self._prepare_documents(request.Documents)
            
            # Process the audit using AI service (legacy method)
            ai_response = await self.ai_service.process_ipm_audit(
                operation=request.Operation,
                products=request.Products,
                documents=documents
            )
            
            # Convert AI response to our response format
            response = AuditProcessResponse(
                ComplianceLevel=ai_response.get("ComplianceLevel", 2),
                Comments=ai_response.get("Comments", ""),
                FilesSearch=[
                    FileSearchResult(
                        FileName=file_info["FileName"],
                        DocumentID=file_info["DocumentID"]
                    )
                    for file_info in ai_response.get("FilesSearch", [])
                ]
            )
            
            logger.info(f"Legacy audit processing completed for AuditID: {request.AuditID}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing legacy audit {request.AuditID}: {e}")
            # Return a default error response
            return AuditProcessResponse(
                ComplianceLevel=2,
                Comments=f"Error processing audit: {str(e)}. Unable to complete compliance assessment.",
                FilesSearch=[]
            )
    
    def _extract_question_ids(self, question_documents: List) -> List[int]:
        """
        Extract unique QuestionIDs from the request.
        
        Args:
            question_documents: List of QuestionDocument objects
            
        Returns:
            List of unique QuestionIDs
        """
        question_ids = []
        for question_doc in question_documents:
            if hasattr(question_doc, 'QuestionID'):
                question_ids.append(question_doc.QuestionID)
        
        # Remove duplicates and return
        return list(set(question_ids))
    
    def _prepare_documents(self, question_documents: List) -> List[Dict[str, Any]]:
        """
        Prepare documents from the request format for AI processing.
        
        Args:
            question_documents: List of QuestionDocument objects
            
        Returns:
            List of document dictionaries for AI processing
        """
        documents = []
        
        # For this implementation, we'll use the example documents provided
        # In a real implementation, you would fetch document content from URLs
        
        # Example documents as provided in the requirements
        example_docs = [
            {
                "FileName": "hola.pdf",
                "content": "este es el contenido del documento weodkew\nwedwe\nwedwe\nwedwe"
            },
            {
                "FileName": "hola2.pdf", 
                "content": "este es el contenido del documento 2\nlinea 1\nlinea 2"
            }
        ]
        
        # In a real implementation, you would:
        # 1. Iterate through question_documents
        # 2. For each document reference, fetch content from the URL
        # 3. Add to documents list
        
        # For now, return the example documents
        return example_docs
    
    async def _fetch_document_content(self, document_url: str) -> str:
        """
        Fetch document content from URL.
        
        Args:
            document_url: URL or path to the document
            
        Returns:
            Document content as string
        """
        # In a real implementation, this would:
        # 1. Download the document from the URL
        # 2. Extract text content (for PDFs, Word docs, etc.)
        # 3. Return the text content
        
        # For now, return placeholder content
        return "Document content would be extracted from the URL in a real implementation."


# Global AI process service instance
ai_process_service = AIProcessService()