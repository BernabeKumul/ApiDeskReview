"""
AI Process endpoints - Handles audit processing requests.
"""
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.ai_process import (
    AuditProcessRequest, 
    AuditProcessResponse, 
    MultipleQuestionsResponse,
    QuestionResponse,
    FileSearchResult
)
from app.services.ai_process_service import ai_process_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/ai-process/audit", 
             response_model=MultipleQuestionsResponse,
             summary="Process Audit Information",
             description="Processes audit information and executes OpenAI API for IPM compliance evaluation with dynamic prompts")
async def process_audit_information(
    request: AuditProcessRequest
) -> MultipleQuestionsResponse:
    """
    Process audit information using AI for IPM compliance evaluation with dynamic prompts.
    
    This endpoint:
    1. Receives audit information including documents and questions
    2. Extracts QuestionIDs from the request
    3. For each QuestionID, loads the corresponding dynamic prompt from JSON
    4. Processes each question separately using OpenAI API
    5. Returns a list of responses, one for each QuestionID
    
    Args:
        request: Audit process request containing:
            - AuditID: Unique audit identifier
            - OrgID: Organization identifier  
            - Operation: Operation name
            - Products: Products being audited
            - Documents: Questions with associated document references (each with QuestionID)
    
    Returns:
        MultipleQuestionsResponse: Contains:
            - success: Boolean indicating success
            - message: Response message
            - data: List of QuestionResponse objects, one for each QuestionID
            - total_questions: Total number of questions processed
    
    Raises:
        HTTPException: If audit processing fails
    """
    try:
        logger.info(f"Received audit processing request for AuditID: {request.AuditID}")
        
        # Validate request
        if not request.Documents:
            logger.warning(f"No documents provided for audit {request.AuditID}")
        
        # Process the audit for multiple questions
        ai_responses = await ai_process_service.process_audit(request)
        
        # Convert AI responses to QuestionResponse objects
        question_responses = []
        for ai_response in ai_responses:
            question_response = QuestionResponse(
                ComplianceLevel=ai_response.get("ComplianceLevel", 2),
                Comments=ai_response.get("Comments", ""),
                FilesSearch=[
                    FileSearchResult(
                        FileName=file_info["FileName"],
                        DocumentID=file_info["DocumentID"]
                    )
                    for file_info in ai_response.get("FilesSearch", [])
                ],
                QuestionID=ai_response.get("QuestionID", "unknown")
            )
            question_responses.append(question_response)
        
        response = MultipleQuestionsResponse(
            success=True,
            message=f"Successfully processed {len(question_responses)} questions for audit {request.AuditID}",
            data=question_responses,
            total_questions=len(question_responses)
        )
        
        logger.info(f"Successfully processed audit {request.AuditID} with {len(question_responses)} questions")
        return response
        
    except Exception as e:
        logger.error(f"Failed to process audit {request.AuditID}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process audit information: {str(e)}"
        )


@router.post("/ai-process/audit-legacy", 
             response_model=AuditProcessResponse,
             summary="Process Audit Information (Legacy)",
             description="Legacy endpoint for backward compatibility - returns single response format")
async def process_audit_information_legacy(
    request: AuditProcessRequest
) -> AuditProcessResponse:
    """
    Legacy endpoint for backward compatibility.
    
    Returns the original single response format instead of the new multiple questions format.
    """
    try:
        logger.info(f"Received legacy audit processing request for AuditID: {request.AuditID}")
        
        # Validate request
        if not request.Documents:
            logger.warning(f"No documents provided for audit {request.AuditID}")
        
        # Process the audit using legacy method
        response = await ai_process_service.process_audit_legacy(request)
        
        logger.info(f"Successfully processed legacy audit {request.AuditID}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to process legacy audit {request.AuditID}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process audit information: {str(e)}"
        )


@router.get("/ai-process/health",
            summary="AI Process Health Check",
            description="Check if AI Process service is running properly")
async def ai_process_health():
    """
    Health check endpoint for AI Process service.
    
    Returns:
        dict: Service status and configuration info
    """
    try:
        # Check if AI service is properly configured
        await ai_process_service.ai_service.initialize()
        
        return {
            "status": "healthy",
            "service": "AIProcess",
            "ai_model": ai_process_service.ai_service.model,
            "message": "AI Process service is running and OpenAI is configured"
        }
    except Exception as e:
        logger.error(f"AI Process health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI Process service health check failed: {str(e)}"
        )