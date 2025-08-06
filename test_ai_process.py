"""
Test script for AI Process endpoint.
"""
import requests
import json

# Test data as specified in the requirements
test_request = {
    "AuditID": 123,
    "OrgID": 456,
    "Operation": "Test Farm Operation",
    "Products": "Strawberries",
    "Documents": [
        {
            "QuestionID": 1,
            "DocumentsId": [
                {
                    "DocumentId": 1,
                    "URL": "https://example.com/hola.pdf"
                },
                {
                    "DocumentId": 2,
                    "URL": "https://example.com/hola2.pdf"
                }
            ]
        }
    ]
}

def test_ai_process_endpoint():
    """Test the AI process endpoint."""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing AI Process Endpoint")
    print("=" * 50)
    
    try:
        # Test health endpoint first
        print("\n1. Testing AI Process Health Check...")
        health_response = requests.get(f"{base_url}/ai-process/health")
        print(f"Health Status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health Response: {health_response.json()}")
        else:
            print(f"Health Error: {health_response.text}")
        
        # Test audit processing endpoint
        print("\n2. Testing Audit Processing...")
        print(f"Request Data: {json.dumps(test_request, indent=2)}")
        
        audit_response = requests.post(
            f"{base_url}/ai-process/audit",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Audit Status: {audit_response.status_code}")
        
        if audit_response.status_code == 200:
            response_data = audit_response.json()
            print(f"✅ Success! Response:")
            print(json.dumps(response_data, indent=2))
            
            # Validate response structure
            assert "ComplianceLevel" in response_data
            assert "Comments" in response_data
            assert "FilesSearch" in response_data
            assert response_data["ComplianceLevel"] == 2
            
            print("\n✅ Response validation passed!")
            
        else:
            print(f"❌ Error: {audit_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_ai_process_endpoint()