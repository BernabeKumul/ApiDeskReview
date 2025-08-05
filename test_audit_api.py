"""
Script de prueba para el API de Auditorías.
Prueba los endpoints del controlador de auditorías y la conexión a SQL Server.
"""
import asyncio
import httpx
import json
from typing import Dict, Any

# Configuración de la prueba
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Datos de prueba (ajustar según tu base de datos)
TEST_AUDIT_HEADER_ID = 1  # Cambiar por un ID válido en tu base de datos
TEST_DOCUMENT_ID = 1      # Cambiar por un ID válido en tu base de datos
TEST_QUESTION_ID = 0


async def test_health_check():
    """Prueba el health check del servicio SQL Server."""
    print("🔍 Probando health check de auditorías...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/audit/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check exitoso: {data['message']}")
                print(f"   Estado: {data['status']}")
                if 'server' in data:
                    print(f"   Servidor: {data['server']}")
                if 'database' in data:
                    print(f"   Base de datos: {data['database']}")
                return True
            else:
                print(f"❌ Health check falló: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return False


async def test_get_audit_documents():
    """Prueba obtener documentos de auditoría."""
    print(f"\n🔍 Probando obtener documentos para audit_header_id={TEST_AUDIT_HEADER_ID}...")
    
    async with httpx.AsyncClient() as client:
        try:
            url = f"{API_BASE}/audit/documents/{TEST_AUDIT_HEADER_ID}"
            
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Documentos obtenidos exitosamente")
                print(f"   Mensaje: {data['message']}")
                print(f"   Total documentos: {data['total_count']}")
                
                if data['data']:
                    print(f"   Primer documento:")
                    first_doc = data['data'][0]
                    for key, value in first_doc.items():
                        if value is not None:
                            print(f"     {key}: {value}")
                
                return data
            else:
                print(f"❌ Error al obtener documentos: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error en obtener documentos: {e}")
            return None


async def test_get_specific_document():
    """Prueba obtener un documento específico."""
    print(f"\n🔍 Probando obtener documento específico {TEST_DOCUMENT_ID}...")
    
    async with httpx.AsyncClient() as client:
        try:
            url = f"{API_BASE}/audit/documents/{TEST_AUDIT_HEADER_ID}/{TEST_DOCUMENT_ID}"
            if TEST_QUESTION_ID != 0:
                url += f"?question_id={TEST_QUESTION_ID}"
            
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Documento específico obtenido: {data['message']}")
                
                if data['data']:
                    print(f"   Detalles del documento:")
                    for key, value in data['data'].items():
                        if value is not None:
                            print(f"     {key}: {value}")
                else:
                    print("   No se encontró el documento")
                
                return data
            else:
                print(f"❌ Error al obtener documento específico: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error en obtener documento específico: {e}")
            return None


async def test_api_documentation():
    """Verifica que la documentación de la API esté disponible."""
    print(f"\n🔍 Verificando documentación de la API...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/docs")
            
            if response.status_code == 200:
                print(f"✅ Documentación disponible en: {BASE_URL}/docs")
                return True
            else:
                print(f"❌ Error al acceder a documentación: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error al verificar documentación: {e}")
            return False


async def test_with_invalid_audit_header():
    """Prueba con un audit_header_id inválido."""
    print(f"\n🔍 Probando con audit_header_id inválido...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE}/audit/documents/0")
            
            if response.status_code == 400:
                print(f"✅ Validación correcta para ID inválido")
                return True
            else:
                print(f"⚠️  Respuesta inesperada para ID inválido: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en prueba de validación: {e}")
            return False


async def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("🚀 Iniciando pruebas del API de Auditorías...")
    print("=" * 60)
    
    # Lista de pruebas
    tests = [
        ("Health Check", test_health_check),
        ("Documentación API", test_api_documentation),
        ("Obtener Documentos", test_get_audit_documents),
        ("Documento Específico", test_get_specific_document),
        ("Validación ID Inválido", test_with_invalid_audit_header),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            result = await test_func()
            results[test_name] = "✅ PASÓ" if result else "❌ FALLÓ"
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results[test_name] = "❌ ERROR"
    
    # Resumen final
    print(f"\n{'=' * 60}")
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    for test_name, result in results.items():
        print(f"{result} {test_name}")
    
    passed = sum(1 for result in results.values() if "✅" in result)
    total = len(results)
    
    print(f"\n🎯 Resultado Final: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    elif passed >= total * 0.8:
        print("✨ Mayoría de pruebas exitosas - implementación funcional")
    else:
        print("⚠️  Algunas pruebas fallaron - revisar configuración")
    
    print(f"\n📚 Para más detalles, visita: {BASE_URL}/docs")


def print_usage_instructions():
    """Imprime instrucciones de uso."""
    print("""
📋 INSTRUCCIONES DE USO:

1. 🔧 CONFIGURACIÓN PREVIA:
   - Asegurar que el servidor esté ejecutándose: python run.py
   - Verificar la conexión a SQL Server en config.py
   - Confirmar que el stored procedure existe en la base de datos

2. 🎯 AJUSTAR DATOS DE PRUEBA:
   - Editar las variables TEST_AUDIT_HEADER_ID y TEST_DOCUMENT_ID
   - Usar IDs válidos de tu base de datos

3. 🚀 EJECUTAR PRUEBAS:
   python test_audit_api.py

4. 📊 PROBAR MANUALMENTE:
   - Abrir http://localhost:8000/docs
   - Usar la interfaz Swagger para probar endpoints
   - Verificar respuestas y códigos de estado

5. 🔍 EJEMPLOS DE CURL:

   # Obtener documentos de auditoría
   curl -X GET "http://localhost:8000/api/v1/audit/documents/1"

   # Health check
   curl -X GET "http://localhost:8000/api/v1/audit/health"

   # Documento específico
   curl -X GET "http://localhost:8000/api/v1/audit/documents/1/101"
""")


if __name__ == "__main__":
    print("🧪 Script de Prueba - API de Auditorías")
    print("=" * 60)
    
    # Verificar si el usuario quiere ver instrucciones
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print_usage_instructions()
    else:
        # Ejecutar las pruebas
        try:
            asyncio.run(run_all_tests())
        except KeyboardInterrupt:
            print("\n⏹️  Pruebas interrumpidas por el usuario")
        except Exception as e:
            print(f"\n💥 Error fatal: {e}")
            print("\nPara obtener ayuda, ejecuta: python test_audit_api.py --help")