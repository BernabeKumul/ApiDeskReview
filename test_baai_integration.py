"""
Script de prueba para la integración completa de BAAI/bge-m3.
Prueba el procesamiento de documentos y búsqueda vectorial.
"""
import asyncio
import json
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar servicios BAAI
from app.services.baai_document_processor import baai_document_processor
from app.services.baai_vector_store import baai_vector_store_service


async def test_baai_integration():
    """Prueba completa de la integración BAAI."""
    
    print("🚀 Iniciando prueba de integración BAAI/bge-m3...")
    
    try:
        # 1. Procesar algunos documentos de prueba
        print("\n📄 Procesando documentos de prueba...")
        result = await baai_document_processor.process_all_documents(limit=5)
        
        print(f"✅ Procesamiento completado:")
        print(f"   - Procesados: {result['processed']}")
        print(f"   - Saltados: {result['skipped']}")
        print(f"   - Errores: {result['errors']}")
        
        if not result['success']:
            print(f"❌ Error en procesamiento: {result['message']}")
            return
        
        # 2. Obtener estadísticas de la colección
        print("\n📊 Obteniendo estadísticas de la colección...")
        await baai_vector_store_service.connect()
        stats = await baai_vector_store_service.get_collection_stats()
        await baai_vector_store_service.disconnect()
        
        print(f"✅ Estadísticas de la colección:")
        print(f"   - Nombre: {stats.get('collection_name', 'N/A')}")
        print(f"   - Puntos: {stats.get('points_count', 0)}")
        print(f"   - Tamaño vector: {stats.get('vector_size', 0)}")
        
        # 3. Probar búsqueda por similitud
        print("\n🔍 Probando búsqueda por similitud...")
        await baai_vector_store_service.connect()
        
        search_results = await baai_vector_store_service.search_similar(
            query_text="steamout resteam",
            limit=3,
            score_threshold=0.5
        )
        
        await baai_vector_store_service.disconnect()
        
        print(f"✅ Búsqueda por similitud completada:")
        print(f"   - Resultados encontrados: {len(search_results)}")
        
        for i, result in enumerate(search_results[:2], 1):
            print(f"   Resultado {i}:")
            print(f"     - Document ID: {result['document_id']}")
            print(f"     - Score: {result['score']:.3f}")
            print(f"     - Contenido: {result['content'][:100]}...")
        
        # 4. Probar búsqueda híbrida
        if search_results:
            document_ids = [search_results[0]['document_id']]
            print(f"\n🔍 Probando búsqueda híbrida con IDs: {document_ids}")
            
            await baai_vector_store_service.connect()
            
            hybrid_results = await baai_vector_store_service.hybrid_search(
                document_ids=document_ids,
                query_text="steamout resteam",
                limit=5,
                score_threshold=0.5
            )
            
            await baai_vector_store_service.disconnect()
            
            print(f"✅ Búsqueda híbrida completada:")
            print(f"   - Resultados encontrados: {len(hybrid_results)}")
            
            for i, result in enumerate(hybrid_results[:2], 1):
                print(f"   Resultado {i}:")
                print(f"     - Document ID: {result['document_id']}")
                print(f"     - Score: {result['score']:.3f}")
                print(f"     - Contenido: {result['content'][:100]}...")
        
        print("\n✅ Prueba de integración BAAI completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en la prueba de integración: {e}")
        logger.error(f"Error en la prueba de integración: {e}")


async def test_baai_endpoints():
    """Prueba los endpoints de BAAI usando requests."""
    
    print("\n🌐 Probando endpoints BAAI...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # 1. Procesar documentos
        print("📄 Probando endpoint de procesamiento...")
        process_data = {
            "process_all": True,
            "limit": 3
        }
        
        response = requests.post(f"{base_url}/baai-search/process", json=process_data)
        print(f"   - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   - Procesados: {result.get('processed', 0)}")
            print(f"   - Saltados: {result.get('skipped', 0)}")
        
        # 2. Obtener estadísticas
        print("\n📊 Probando endpoint de estadísticas...")
        response = requests.get(f"{base_url}/baai-search/stats")
        print(f"   - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   - Éxito: {result.get('success', False)}")
            if result.get('stats'):
                stats = result['stats']
                print(f"   - Puntos: {stats.get('points_count', 0)}")
        
        # 3. Búsqueda por similitud
        print("\n🔍 Probando búsqueda por similitud...")
        response = requests.get(
            f"{base_url}/baai-search/search/similar",
            params={
                "query_text": "steamout resteam",
                "limit": 3,
                "score_threshold": 0.5
            }
        )
        print(f"   - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   - Resultados: {result.get('total_results', 0)}")
        
        print("\n✅ Prueba de endpoints BAAI completada!")
        
    except Exception as e:
        print(f"❌ Error probando endpoints: {e}")


if __name__ == "__main__":
    print("🧪 Iniciando pruebas de integración BAAI/bge-m3...")
    
    # Ejecutar pruebas
    asyncio.run(test_baai_integration())
    
    # Comentar la siguiente línea si no tienes el servidor corriendo
    # asyncio.run(test_baai_endpoints())
    
    print("\n🎉 Pruebas completadas!") 