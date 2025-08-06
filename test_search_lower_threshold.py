"""
Script para probar búsquedas con umbral más bajo.
"""
import asyncio
import logging
from app.services.vector_store import vector_store_service

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search_lower_threshold():
    """Prueba búsquedas con umbral más bajo."""
    try:
        print("🔍 Probando búsquedas con umbral más bajo...")
        
        # Conectar a Qdrant
        await vector_store_service.connect()
        
        # Obtener estadísticas
        stats = await vector_store_service.get_collection_stats()
        print(f"📊 Colección: {stats.get('name', 'N/A')}")
        print(f"   📈 Puntos totales: {stats.get('points_count', 0)}")
        
        # Prueba 1: Búsqueda por "room" con umbral bajo
        print("\n🔍 Prueba 1: Búsqueda por 'room'")
        
        results = await vector_store_service.search_similar(
            query_text="room",
            limit=10,
            score_threshold=0.1  # Umbral muy bajo
        )
        
        print(f"✅ Resultados: {len(results)}")
        for i, result in enumerate(results[:5], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
        # Prueba 2: Búsqueda por "temperature" con umbral bajo
        print("\n🔍 Prueba 2: Búsqueda por 'temperature'")
        
        temp_results = await vector_store_service.search_similar(
            query_text="temperature",
            limit=10,
            score_threshold=0.1
        )
        
        print(f"✅ Resultados: {len(temp_results)}")
        for i, result in enumerate(temp_results[:5], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
        # Prueba 3: Búsqueda por "crop" con umbral bajo
        print("\n🔍 Prueba 3: Búsqueda por 'crop'")
        
        crop_results = await vector_store_service.search_similar(
            query_text="crop",
            limit=10,
            score_threshold=0.1
        )
        
        print(f"✅ Resultados: {len(crop_results)}")
        for i, result in enumerate(crop_results[:5], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
        # Prueba 4: Búsqueda híbrida con umbral bajo
        print("\n🔍 Prueba 4: Búsqueda híbrida por 'room'")
        print("Documentos: [702903, 727656]")
        
        hybrid_results = await vector_store_service.search_by_document_ids(
            document_ids=[702903, 727656],
            query_text="room",
            limit=10
        )
        
        print(f"✅ Resultados híbridos: {len(hybrid_results)}")
        for i, result in enumerate(hybrid_results[:5], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
        # Prueba 5: Búsqueda por "humidity" con umbral bajo
        print("\n🔍 Prueba 5: Búsqueda por 'humidity'")
        
        humidity_results = await vector_store_service.search_similar(
            query_text="humidity",
            limit=10,
            score_threshold=0.1
        )
        
        print(f"✅ Resultados: {len(humidity_results)}")
        for i, result in enumerate(humidity_results[:5], 1):
            print(f"   {i}. Score: {result['score']:.3f}")
            print(f"      Doc: {result['metadata']['DocumentId']}")
            print(f"      Texto: {result['text'][:100]}...")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
    finally:
        await vector_store_service.disconnect()
        print("\n✅ Pruebas de búsqueda completadas")

if __name__ == "__main__":
    asyncio.run(test_search_lower_threshold()) 