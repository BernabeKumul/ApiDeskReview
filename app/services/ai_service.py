"""
AI service - OpenAI integration.
Handles IPM compliance auditing using OpenAI.
"""
import json
import os
from typing import List, Dict, Any
from app.core.config import settings
from app.utils.logger import logger


class AIService:
    """
    OpenAI AI service for IPM compliance auditing.
    This class handles OpenAI API interactions for audit processing.
    """
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
        self.client = None
        self.dynamic_prompts = self._load_dynamic_prompts()
    
    def _load_dynamic_prompts(self) -> Dict[str, str]:
        """Load dynamic prompts from JSON file."""
        try:
            # Get the path to the JSON file relative to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(current_dir, '..', '..')
            json_path = os.path.join(project_root, 'JSON', 'AzzuleAI.AIDynamicPrompts.json')
            
            with open(json_path, 'r', encoding='utf-8') as file:
                prompts_data = json.load(file)
            
            # Create a dictionary mapping NameSection to Text
            prompts_dict = {}
            for prompt in prompts_data:
                prompts_dict[prompt['NameSection']] = prompt['Text']
            
            logger.info(f"📝 Loaded {len(prompts_dict)} dynamic prompts")
            return prompts_dict
            
        except Exception as e:
            logger.error(f"Failed to load dynamic prompts: {e}")
            return {}
    
    async def initialize(self):
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            logger.info(f"🤖 OpenAI service configured with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI service: {e}")
            raise
    
    def _create_dynamic_prompt(self, question_id: str, operation: str, products: str, documents: List[Dict[str, Any]]) -> str:
        """Create a dynamic IPM compliance audit prompt based on QuestionID."""
        
        # Get the specific prompt for this question
        specific_prompt = self.dynamic_prompts.get(question_id, "")
        
        if not specific_prompt:
            logger.warning(f"No dynamic prompt found for QuestionID: {question_id}")
            specific_prompt = "Question not found in dynamic prompts. Please provide compliance assessment based on available documentation."
        
        # Base prompt for IPM auditing
        base_prompt = f"""Act as an IPM Compliance Auditor. Evaluate compliance with PrimusGFS Module 9 – Integrated Pest Management (IPM) Practices strictly based on the uploaded documents.
- Do not assume compliance where documentation is missing or unclear
- Do not offer suggestions or improvements
- Focus only on determining if the documents meet compliance expectations
- Use all documents provided, even duplicates or scans with limited content

Write detailed, structured compliance summaries in a professional, audit-style format. Your summaries should reference:
- Document names (including file extensions)
- Document sections or content descriptions
- Relevant dates and timeframes
- Personnel or titles when identified

If documentation is missing or insufficient, clearly state this and explain why the operation is considered non-compliant.

For the purpose of this exercise, consider {products} as the product of the audit and {operation} as the audited operation.

General Response Format for Each Question
Each response must include:
1. Summary of key compliance findings, citing document names and details
2. Clear statement of any missing or insufficient elements
3. Explanation if submitted documents were not used (e.g., "Farm work logs were submitted but did not contain relevant information for this question.")
4. Multiple paragraphs, each focused on a specific theme (e.g., pest monitoring, thresholds, non-chemical controls)
5. Response must not exceed 2,000 characters
6. Always use the exact document file name (e.g., IPMPlan2023.pdf) — do not shorten or summarize
7. Write in English

{specific_prompt}

Provides a json response with the following keys:
1. ComplianceLevel: Always returns the value 2.
2. Comments: Break the response into multiple paragraphs. Each paragraph should focus on a specific aspect described above.
3. FilesSearch: return a JSON with the FileName and DocumentID, returns an empty array in case no files are sent
4. QuestionID: Return the QuestionID that was processed ({question_id})

Documents:
"""
        
        # Add document content to the prompt
        for doc in documents:
            base_prompt += f"\nFileName: {doc['FileName']}\n"
            base_prompt += f"content: {doc['content']}\n"
        
        return base_prompt
    
    def _create_ipm_prompt(self, operation: str, products: str, documents: List[Dict[str, Any]]) -> str:
        """Create the IPM compliance audit prompt (legacy method for backward compatibility)."""
        # Use the dynamic prompt with default QuestionID 4346
        return self._create_dynamic_prompt("4346", operation, products, documents)
    
    async def process_multiple_questions(self, operation: str, products: str, question_ids: List[str], documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple QuestionIDs and return a list of responses."""
        responses = []
        
        for question_id in question_ids:
            try:
                logger.info(f"Processing QuestionID: {question_id}")
                
                # Create prompt for this specific question
                prompt = self._create_dynamic_prompt(question_id, operation, products, documents)
                
                # Process with OpenAI or simulate
                if self.api_key == "xx":
                    # Placeholder response when using demo key
                    response = await self._simulate_audit_response_with_question_id(documents, question_id)
                else:
                    # Use real OpenAI API
                    try:
                        response = await self._call_openai_api_with_question_id(prompt, documents, question_id)
                    except Exception as e:
                        logger.warning(f"OpenAI API call failed for QuestionID {question_id}, using simulation: {e}")
                        response = await self._simulate_audit_response_with_question_id(documents, question_id)
                
                responses.append(response)
                
            except Exception as e:
                logger.error(f"Error processing QuestionID {question_id}: {e}")
                # Add error response for this question
                responses.append({
                    "ComplianceLevel": 2,
                    "Comments": f"Error processing QuestionID {question_id}: {str(e)}",
                    "FilesSearch": [],
                    "QuestionID": question_id
                })
        
        return responses
    
    async def process_ipm_audit(self, operation: str, products: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process IPM audit using OpenAI (legacy method for backward compatibility)."""
        try:
            prompt = self._create_ipm_prompt(operation, products, documents)
            
            # In a real implementation, this would call OpenAI API
            # For now, we'll simulate the response based on the provided documents
            
            #logger.info(f"Processing IPM audit for operation: {operation}")
            
            # Process with OpenAI or simulate
            if self.api_key == "xx":
                # Placeholder response when using demo key
                response = await self._simulate_audit_response(documents)
            else:
                # Use real OpenAI API
                try:
                    response = await self._call_openai_api(prompt, documents)
                except Exception as e:
                    logger.warning(f"OpenAI API call failed, using simulation: {e}")
                    response = await self._simulate_audit_response(documents)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing IPM audit: {e}")
            raise
    
    async def _simulate_audit_response_with_question_id(self, documents: List[Dict[str, Any]], question_id: str) -> Dict[str, Any]:
        """Simulate audit response for demonstration purposes with QuestionID."""
        
        # Create files search list from provided documents
        files_search = []
        for doc in documents:
            files_search.append({
                "FileName": doc["FileName"],
                "DocumentID": doc["FileName"]
            })
        
        # Generate compliance comments based on documents and question
        if documents:
            comments = self._generate_compliance_comments_for_question(documents, question_id)
        else:
            comments = (f"No documents were provided for QuestionID {question_id}. "
                       "Without proper documentation, compliance cannot be verified. "
                       "The operation must provide adequate documentation to meet PrimusGFS Module 9 requirements.")
        
        return {
            "ComplianceLevel": 2,
            "Comments": comments,
            "FilesSearch": files_search,
            "QuestionID": question_id
        }
    
    async def _simulate_audit_response(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate audit response for demonstration purposes (legacy method)."""
        
        # Create files search list from provided documents
        files_search = []
        for doc in documents:
            files_search.append({
                "FileName": doc["FileName"],
                "DocumentID": doc["FileName"]
            })
        
        # Generate compliance comments based on documents
        if documents:
            comments = self._generate_compliance_comments(documents)
        else:
            comments = ("No documents were provided for this audit. "
                       "Without proper documentation, compliance cannot be verified. "
                       "The operation must provide a documented IPM plan to meet PrimusGFS Module 9 requirements.")
        
        return {
            "ComplianceLevel": 2,
            "Comments": comments,
            "FilesSearch": files_search
        }
    
    def _generate_compliance_comments(self, documents: List[Dict[str, Any]]) -> str:
        """Generate compliance comments based on available documents."""
        
        comments_parts = []
        
        # Analyze document availability
        doc_names = [doc["FileName"] for doc in documents]
        
        comments_parts.append(
            f"The operation has submitted {len(documents)} document(s) for review: {', '.join(doc_names)}. "
            f"Upon examination of the provided documentation, the following compliance assessment is made."
        )
        
        # Analyze content (simplified for demonstration)
        has_substantial_content = any(len(doc.get("content", "")) > 50 for doc in documents)
        
        if has_substantial_content:
            comments_parts.append(
                "The submitted documents contain operational information. However, a comprehensive IPM plan "
                "should specifically address pest monitoring practices, action thresholds, prevention strategies, "
                "and pollinator protection measures as required by PrimusGFS Module 9."
            )
            
            comments_parts.append(
                "To achieve full compliance, the operation should ensure all IPM plan components are clearly "
                "documented, including specific monitoring protocols, defined treatment thresholds, and "
                "environmental protection strategies."
            )
        else:
            comments_parts.append(
                "The submitted documents appear to contain limited content relevant to IPM practices. "
                "A complete IPM plan must include detailed pest monitoring procedures, economic thresholds, "
                "prevention methods, and resistance management strategies."
            )
            
            comments_parts.append(
                "The current documentation is insufficient to demonstrate compliance with PrimusGFS Module 9 "
                "requirements. Additional documentation outlining comprehensive IPM practices is required."
            )
        
        return " ".join(comments_parts)
    
    def _generate_compliance_comments_for_question(self, documents: List[Dict[str, Any]], question_id: str) -> str:
        """Generate compliance comments based on available documents for a specific question."""
        
        comments_parts = []
        
        # Get question-specific information
        question_prompt = self.dynamic_prompts.get(question_id, "")
        question_title = "Unknown Question"
        
        if question_prompt:
            # Extract question title from the prompt
            lines = question_prompt.split('\n')
            if lines:
                question_title = lines[0].strip()
        
        # Analyze document availability
        doc_names = [doc["FileName"] for doc in documents]
        
        comments_parts.append(
            f"Assessment for {question_title} (QuestionID: {question_id}). "
            f"The operation has submitted {len(documents)} document(s) for review: {', '.join(doc_names)}. "
            f"Upon examination of the provided documentation, the following compliance assessment is made."
        )
        
        # Analyze content (simplified for demonstration)
        has_substantial_content = any(len(doc.get("content", "")) > 50 for doc in documents)
        
        if has_substantial_content:
            comments_parts.append(
                f"The submitted documents contain operational information relevant to {question_title}. "
                "However, comprehensive compliance documentation should address all specific requirements "
                "outlined in the PrimusGFS Module 9 standards for this question."
            )
            
            comments_parts.append(
                "To achieve full compliance, the operation should ensure all required elements are clearly "
                "documented and demonstrate adherence to the specific criteria for this assessment area."
            )
        else:
            comments_parts.append(
                f"The submitted documents appear to contain limited content relevant to {question_title}. "
                "Complete documentation must include detailed information addressing all requirements "
                "specified for this particular assessment criterion."
            )
            
            comments_parts.append(
                f"The current documentation is insufficient to demonstrate compliance with the specific "
                f"requirements of {question_title}. Additional comprehensive documentation is required."
            )
        
        return " ".join(comments_parts)
    
    async def _call_openai_api_with_question_id(self, prompt: str, documents: List[Dict[str, Any]], question_id: str) -> Dict[str, Any]:
        """Call OpenAI API for IPM compliance evaluation with QuestionID."""
        try:
            if not self.client:
                await self.initialize()
            
            # Create system and user messages
            system_message = {
                "role": "system",
                "content": f"You are an IPM Compliance Auditor specializing in PrimusGFS Module 9. Provide detailed, professional audit assessments in JSON format for QuestionID {question_id}."
            }
            
            user_message = {
                "role": "user", 
                "content": prompt
            }

            logger.info(f"PROMPT for QuestionID {question_id}: {prompt}")
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[system_message, user_message],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            #logger.info(f"OpenAI response received for QuestionID {question_id}: {len(content)} characters")
            
            # Try to parse JSON response
            try:
                ai_response = json.loads(content)
                
                # Ensure required fields are present and properly formatted
                if "ComplianceLevel" not in ai_response:
                    ai_response["ComplianceLevel"] = 2
                
                if "FilesSearch" not in ai_response:
                    ai_response["FilesSearch"] = [
                        {"FileName": doc["FileName"], "DocumentID": doc["FileName"]} 
                        for doc in documents
                    ]
                
                if "QuestionID" not in ai_response:
                    ai_response["QuestionID"] = question_id
                
                # Ensure Comments is a string (not a list)
                if "Comments" in ai_response:
                    comments = ai_response["Comments"]
                    if isinstance(comments, list):
                        ai_response["Comments"] = " ".join(str(item) for item in comments)
                    elif not isinstance(comments, str):
                        ai_response["Comments"] = str(comments)
                
                # Ensure QuestionID is a string
                if "QuestionID" in ai_response and not isinstance(ai_response["QuestionID"], str):
                    ai_response["QuestionID"] = str(ai_response["QuestionID"])
                
                return ai_response
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI JSON response for QuestionID {question_id}: {e}")
                # Fallback to simulation
                return await self._simulate_audit_response_with_question_id(documents, question_id)
                
        except Exception as e:
            logger.error(f"OpenAI API call failed for QuestionID {question_id}: {e}")
            raise
    
    async def _call_openai_api(self, prompt: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Call OpenAI API for IPM compliance evaluation."""
        try:
            if not self.client:
                await self.initialize()
            
            # Create system and user messages
            system_message = {
                "role": "system",
                "content": "You are an IPM Compliance Auditor specializing in PrimusGFS Module 9. Provide detailed, professional audit assessments in JSON format."
            }
            
            user_message = {
                "role": "user", 
                "content": prompt
            }

            logger.info(f"PROMPT: {prompt}")
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[system_message, user_message],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            logger.info(f"OpenAI response received: {len(content)} characters")
            
            # Try to parse JSON response
            try:
                ai_response = json.loads(content)
                
                # Ensure required fields are present and properly formatted
                if "ComplianceLevel" not in ai_response:
                    ai_response["ComplianceLevel"] = 2
                
                if "FilesSearch" not in ai_response:
                    ai_response["FilesSearch"] = [
                        {"FileName": doc["FileName"], "DocumentID": doc["FileName"]} 
                        for doc in documents
                    ]
                
                # Ensure Comments is a string (not a list)
                if "Comments" in ai_response:
                    comments = ai_response["Comments"]
                    if isinstance(comments, list):
                        ai_response["Comments"] = " ".join(str(item) for item in comments)
                    elif not isinstance(comments, str):
                        ai_response["Comments"] = str(comments)
                
                return ai_response
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI JSON response: {e}")
                # Fallback to simulation
                return await self._simulate_audit_response(documents)
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    async def generate_completion(self, prompt: str, max_tokens: int = None):
        """Generate text completion using OpenAI."""
        max_tokens = max_tokens or self.max_tokens
        logger.info(f"🤖 Generating completion for prompt: {prompt[:50]}...")
        
        # Placeholder implementation
        return {
            "response": "This is a placeholder response from AI service",
            "tokens_used": 0
        }
    
    async def generate_embeddings(self, text: str):
        """Generate embeddings for text using OpenAI."""
        logger.info(f"🤖 Generating embeddings for text: {text[:50]}...")
        return [0.0] * 1536  # Placeholder embedding vector
    
    async def chat_completion(self, messages: list):
        """Generate chat completion using OpenAI."""
        logger.info(f"🤖 Processing chat with {len(messages)} messages")
        return {
            "response": "This is a placeholder chat response",
            "tokens_used": 0
        }


# Global AI service instance
ai_service = AIService()