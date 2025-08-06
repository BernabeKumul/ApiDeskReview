"""
Script de prueba para verificar el procesamiento de vectores.
"""
import asyncio
import logging
from pathlib import Path

from app.services.vector_store import vector_store_service
from app.services.embedding_service import embedding_service

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_embeddings():
    """Prueba el servicio de embeddings."""
    print("🧪 Probando servicio de embeddings...")
    
    # Texto de prueba
    test_text = "Next Crop: 29\nRoom: 308\nTemperature: 22°C\nHumidity: 65%"
    
    # Procesar documento de prueba
    metadata = {
        'DocumentId': 999999,
        'FileName': 'test_document.pdf',
        'DocumentType': 'Test',
        'TotalReading': 0,
        'CreatedAt': '2025-01-01T00:00:00Z',
        'UpdatedAt': '2025-01-01T00:00:00Z',
        'Inactive': False
    }
    
    chunks = embedding_service.process_document(test_text, metadata)
    
    print(f"✅ Embeddings generados: {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i}: {len(chunk['embedding'])} dimensiones")
        print(f"   Texto: {chunk['text'][:50]}...")
    
    return chunks

async def test_qdrant_connection():
    """Prueba la conexión a Qdrant."""
    print("\n🔍 Probando conexión a Qdrant...")
    
    try:
        await vector_store_service.connect()
        await vector_store_service.create_collection()
        
        # Obtener estadísticas
        stats = await vector_store_service.get_collection_stats()
        print(f"✅ Conexión exitosa a Qdrant")
        print(f"   Colección: {stats.get('name', 'N/A')}")
        print(f"   Puntos: {stats.get('points_count', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Error conectando a Qdrant: {e}")
        return False

async def test_document_processing():
    """Prueba el procesamiento de un documento."""
    print("\n📄 Probando procesamiento de documento...")
    
    # Verificar si el documento ya existe
    test_doc_id = 999999
    exists = await vector_store_service.document_exists(test_doc_id)
    print(f"Documento {test_doc_id} existe: {exists}")
    
    if not exists:
        # Procesar documento de prueba
        test_text = "This is a test document for vector processing. It contains multiple sentences to test chunking and embedding generation."
        
        metadata = {
            'DocumentId': test_doc_id,
            'FileName': 'test_document.pdf',
            'DocumentType': 'Test',
            'TotalReading': 0,
            'CreatedAt': '2025-01-01T00:00:00Z',
            'UpdatedAt': '2025-01-01T00:00:00Z',
            'Inactive': False
        }
        
        chunks = embedding_service.process_document(test_text, metadata)
        
        if chunks:
            success = await vector_store_service.insert_document_chunks(chunks)
            if success:
                print(f"✅ Documento insertado: {len(chunks)} chunks")
            else:
                print("❌ Error insertando documento")
        else:
            print("❌ No se generaron chunks")
    else:
        print("🔄 Documento ya existe, saltando inserción")

async def test_search():
    """Prueba la búsqueda híbrida."""
    print("\n🔍 Probando búsqueda híbrida...")
    
    try:
        # Búsqueda por similitud
        results = await vector_store_service.search_similar(
            query_text="test document",
            limit=5
        )
        
        print(f"✅ Búsqueda por similitud: {len(results)} resultados")
        
        if results:
            print("📋 Primeros resultados:")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. Score: {result['score']:.3f}")
                print(f"      Doc: {result['metadata']['DocumentId']}")
                print(f"      Texto: {result['text'][:50]}...")
        
        # Búsqueda híbrida
        hybrid_results = await vector_store_service.search_by_document_ids(
            document_ids=[999999],
            query_text="test",
            limit=5
        )
        
        print(f"✅ Búsqueda híbrida: {len(hybrid_results)} resultados")
        
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")

async def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas de vector processing...")
    
    try:
        # Probar embeddings
        await test_embeddings()
        
        # Probar conexión Qdrant
        if await test_qdrant_connection():
            # Probar procesamiento
            await test_document_processing()
            
            # Probar búsqueda
            await test_search()
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
    finally:
        # Desconectar
        await vector_store_service.disconnect()
        print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main()) 