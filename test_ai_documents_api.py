"""
Script de prueba para la API de documentos de IA.
Ejecutar después de iniciar el servidor FastAPI.
"""
import asyncio
import httpx
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api/v1"

async def test_ai_documents_api():
    """Prueba completa de la API de documentos de IA."""
    
    async with httpx.AsyncClient() as client:
        print("🧪 Iniciando pruebas de la API de documentos de IA\n")
        
        # 1. Verificar health check
        print("1️⃣ Verificando estado de salud...")
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("\n" + "="*50 + "\n")
        
        # 2. Verificar estado específico de MongoDB
        print("2️⃣ Verificando estado de MongoDB...")
        response = await client.get(f"{BASE_URL}/health/mongodb")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("\n" + "="*50 + "\n")
        
        # 3. Crear un documento de prueba
        print("3️⃣ Creando documento de prueba...")
        test_document = {
            "document_id": 999999,
            "file_name": "TEST_DOCUMENT.pdf",
            "document_type": "Test",
            "content": "Este es un documento de prueba creado por el script de testing. Contiene información de ejemplo para validar la funcionalidad de la API.",
            "total_reading": 0,
            "inactive": False
        }
        
        response = await client.post(
            f"{BASE_URL}/ai-documents/",
            json=test_document
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Obtener el ID del documento creado
        document_id = None
        if response.status_code == 201:
            document_id = response.json()["data"]["document_id"]
            print(f"✅ Documento creado con ID: {document_id}")
        print("\n" + "="*50 + "\n")
        
        # 4. Buscar documento por filtros
        print("4️⃣ Buscando documento por filtros...")
        response = await client.get(
            f"{BASE_URL}/ai-documents/search",
            params={
                "file_name": "TEST_DOCUMENT.pdf",
                "document_id": 999999
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("\n" + "="*50 + "\n")
        
        # 5. Obtener todos los documentos
        print("5️⃣ Obteniendo todos los documentos (página 1)...")
        response = await client.get(
            f"{BASE_URL}/ai-documents/",
            params={
                "page": 1,
                "page_size": 5,
                "sort_by": "CreatedAt",
                "sort_order": "desc"
            }
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Total documentos encontrados: {result.get('total_count', 'N/A')}")
        print(f"Documentos en esta página: {len(result.get('data', []))}")
        print("\n" + "="*50 + "\n")
        
        # 6. Buscar por contenido
        print("6️⃣ Buscando documentos por contenido...")
        response = await client.get(
            f"{BASE_URL}/ai-documents/search/content",
            params={
                "search_term": "prueba",
                "page": 1,
                "page_size": 10
            }
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Documentos encontrados con 'prueba': {len(result.get('data', []))}")
        print("\n" + "="*50 + "\n")
        
        # 7. Actualizar documento (si se creó exitosamente)
        if document_id:
            print("7️⃣ Actualizando documento de prueba...")
            update_data = {
                "content": "Contenido actualizado para el documento de prueba. Actualizado el " + datetime.now().isoformat(),
                "total_reading": 1
            }
            
            response = await client.put(
                f"{BASE_URL}/ai-documents/{document_id}",
                json=update_data
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("\n" + "="*50 + "\n")
            
            # 8. Obtener documento actualizado por ID
            print("8️⃣ Obteniendo documento actualizado por ID...")
            response = await client.get(f"{BASE_URL}/ai-documents/{document_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                doc_data = response.json()["data"]
                print(f"Documento: {doc_data['file_name']}")
                print(f"Total Reading: {doc_data['total_reading']}")
                print(f"Última actualización: {doc_data['updated_at']}")
            print("\n" + "="*50 + "\n")
            
            # 9. Eliminación lógica
            print("9️⃣ Realizando eliminación lógica...")
            response = await client.patch(f"{BASE_URL}/ai-documents/{document_id}/soft-delete")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("\n" + "="*50 + "\n")
            
            # 10. Verificar eliminación lógica
            print("🔟 Verificando eliminación lógica...")
            response = await client.get(f"{BASE_URL}/ai-documents/{document_id}")
            if response.status_code == 200:
                doc_data = response.json()["data"]
                print(f"Documento inactivo: {doc_data['inactive']}")
            print("\n" + "="*50 + "\n")
            
            # 11. Eliminación física (opcional - descomenta para probar)
            # print("🗑️ Eliminando documento físicamente...")
            # response = await client.delete(f"{BASE_URL}/ai-documents/{document_id}")
            # print(f"Status: {response.status_code}")
            # print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        print("✅ Pruebas completadas!")

async def test_error_cases():
    """Prueba casos de error comunes."""
    
    async with httpx.AsyncClient() as client:
        print("\n🚨 Probando casos de error...\n")
        
        # Documento no encontrado
        print("❌ Buscando documento inexistente...")
        response = await client.get(f"{BASE_URL}/ai-documents/507f1f77bcf86cd799439011")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("\n" + "="*50 + "\n")
        
        # Búsqueda sin filtros
        print("❌ Búsqueda sin filtros...")
        response = await client.get(f"{BASE_URL}/ai-documents/search")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("\n" + "="*50 + "\n")
        
        # Crear documento con DocumentId duplicado
        print("❌ Creando documento con DocumentId duplicado...")
        duplicate_document = {
            "document_id": 999999,  # Mismo ID que antes
            "file_name": "DUPLICATE_TEST.pdf",
            "document_type": "Test",
            "content": "Documento duplicado",
            "total_reading": 0,
            "inactive": False
        }
        
        response = await client.post(
            f"{BASE_URL}/ai-documents/",
            json=duplicate_document
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("🚀 Iniciando script de pruebas para AI Documents API")
    print("📋 Asegúrate de que el servidor FastAPI esté ejecutándose en http://localhost:8000")
    print("=" * 80)
    
    # Ejecutar pruebas principales
    asyncio.run(test_ai_documents_api())
    
    # Ejecutar pruebas de errores
    asyncio.run(test_error_cases())
    
    print("\n🎉 Script de pruebas finalizado!")