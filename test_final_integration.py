"""
Test final de integración para el endpoint AIProcess con OpenAI.
"""
import requests
import json
import time

# Datos de prueba según especificaciones
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

def test_ai_process_integration():
    """Prueba la integración completa del endpoint AIProcess."""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 PRUEBA DE INTEGRACIÓN COMPLETA - AIProcess con OpenAI")
    print("=" * 60)
    
    # Esperar a que el servidor inicie
    print("\n⏳ Esperando que el servidor inicie...")
    time.sleep(8)
    
    try:
        # 1. Verificar health check del AI Process
        print("\n1. 🔍 Verificando AI Process Health Check...")
        health_response = requests.get(f"{base_url}/ai-process/health", timeout=10)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health Check exitoso:")
            print(f"   - Estado: {health_data.get('status')}")
            print(f"   - Modelo AI: {health_data.get('ai_model')}")
            print(f"   - Mensaje: {health_data.get('message')}")
        else:
            print(f"❌ Health Check falló: {health_response.status_code}")
            return
        
        # 2. Probar el endpoint principal de procesamiento
        print(f"\n2. 🤖 Probando endpoint de procesamiento de auditoría...")
        print(f"   Request: {json.dumps(test_request, indent=2)}")
        
        audit_response = requests.post(
            f"{base_url}/ai-process/audit",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n   Status Code: {audit_response.status_code}")
        
        if audit_response.status_code == 200:
            response_data = audit_response.json()
            print(f"\n✅ ¡ÉXITO! Respuesta del procesamiento:")
            print(f"   ComplianceLevel: {response_data.get('ComplianceLevel')}")
            print(f"   Comments: {response_data.get('Comments')[:200]}...")
            print(f"   FilesSearch: {response_data.get('FilesSearch')}")
            
            # Validar estructura de respuesta
            assert "ComplianceLevel" in response_data, "Falta ComplianceLevel"
            assert "Comments" in response_data, "Falta Comments"
            assert "FilesSearch" in response_data, "Falta FilesSearch"
            assert response_data["ComplianceLevel"] == 2, "ComplianceLevel debe ser 2"
            
            print(f"\n✅ Validación de estructura exitosa!")
            
            # Mostrar respuesta completa formateada
            print(f"\n📋 RESPUESTA COMPLETA:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ Error en procesamiento: {audit_response.status_code}")
            print(f"   Respuesta: {audit_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: Asegúrate de que el servidor esté corriendo en http://127.0.0.1:8000")
    except requests.exceptions.Timeout:
        print("❌ Timeout: El servidor tardó demasiado en responder")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_ai_process_integration()