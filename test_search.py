"""
Script para probar búsquedas híbridas con datos reales.
"""
import asyncio
import logging
from app.services.vector_store import vector_store_service

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_hybrid_search():
    """Prueba búsquedas híbridas con datos reales."""
    try:
        print("🔍 Probando búsquedas híbridas con datos reales...")
        
        # Conectar a Qdrant
        await vector_store_service.connect()
        
        # Obtener estadísticas
        stats = await vector_store_service.get_collection_stats()
        print(f"📊 Colección: {stats.get('name', 'N/A')}")
        print(f"   📈 Puntos totales: {stats.get('points_count', 0)}")
        
        # Prueba 1: Búsqueda por similitud general
        print("\n🔍 Prueba 1: Búsqueda por similitud general")
        print("Query: 'Room 308'")
        
        results = await vector_store_service.search_similar(
            query_text="Room 308",
            limit=5
        )
        
        print(f"✅ Resultados: {len(results)}")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
        # Prueba 2: Búsqueda híbrida en documentos específicos
        print("\n🔍 Prueba 2: Búsqueda híbrida")
        print("Documentos: [702903, 727656]")
        print("Query: 'Room 308'")
        
        hybrid_results = await vector_store_service.search_by_document_ids(
            document_ids=[702903, 727656],
            query_text="Room 308",
            limit=5
        )
        
        print(f"✅ Resultados híbridos: {len(hybrid_results)}")
        for i, result in enumerate(hybrid_results[:3], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
        # Prueba 3: Búsqueda por temperatura
        print("\n🔍 Prueba 3: Búsqueda por temperatura")
        print("Query: 'temperature 22'")
        
        temp_results = await vector_store_service.search_similar(
            query_text="temperature 22",
            limit=5
        )
        
        print(f"✅ Resultados: {len(temp_results)}")
        for i, result in enumerate(temp_results[:3], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
        # Prueba 4: Búsqueda híbrida por crop
        print("\n🔍 Prueba 4: Búsqueda híbrida por crop")
        print("Documentos: [747575, 750980]")
        print("Query: 'crop 29'")
        
        crop_results = await vector_store_service.search_by_document_ids(
            document_ids=[747575, 750980],
            query_text="crop 29",
            limit=5
        )
        
        print(f"✅ Resultados híbridos: {len(crop_results)}")
        for i, result in enumerate(crop_results[:3], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
        # Prueba 5: Búsqueda por humedad
        print("\n🔍 Prueba 5: Búsqueda por humedad")
        print("Query: 'humidity 65'")
        
        humidity_results = await vector_store_service.search_similar(
            query_text="humidity 65",
            limit=5
        )
        
        print(f"✅ Resultados: {len(humidity_results)}")
        for i, result in enumerate(humidity_results[:3], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
    finally:
        await vector_store_service.disconnect()
        print("\n✅ Pruebas de búsqueda completadas")

if __name__ == "__main__":
    asyncio.run(test_hybrid_search()) 