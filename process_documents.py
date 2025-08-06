"""
Script para procesar documentos JSON a Qdrant con verificación de duplicados.
"""
import asyncio
import logging
from pathlib import Path

from app.services.vector_store import vector_store_service
from app.services.document_processor import document_processor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Función principal de procesamiento."""
    try:
        print("🚀 Iniciando procesamiento de documentos a Qdrant...")
        
        # Conectar a Qdrant
        await vector_store_service.connect()
        await vector_store_service.create_collection()
        
        # Ruta al archivo JSON
        json_file = Path("JSON/AzzuleAI.AIDocuments.json")
        
        if not json_file.exists():
            logger.error(f"Archivo no encontrado: {json_file}")
            print(f"❌ Archivo no encontrado: {json_file}")
            return
        
        print(f"📄 Archivo encontrado: {json_file}")
        
        # Procesar todos los documentos
        stats = await document_processor.process_json_file(str(json_file))
        
        # Mostrar estadísticas
        print("\n📊 Estadísticas del procesamiento:")
        print(f"   ✅ Procesados: {stats['processed']}")
        print(f"   ⏭️  Saltados (duplicados): {stats['skipped']}")
        print(f"   ❌ Errores: {stats['errors']}")
        print(f"   📄 Total: {stats['total']}")
        
        # Obtener estadísticas de Qdrant
        qdrant_stats = await vector_store_service.get_collection_stats()
        print(f"\n📊 Qdrant - Colección: {qdrant_stats.get('name', 'N/A')}")
        print(f"   📈 Puntos totales: {qdrant_stats.get('points_count', 0)}")
        print(f"   🔢 Vectores: {qdrant_stats.get('vectors_count', 0)}")
        print(f"   📊 Estado: {qdrant_stats.get('status', 'N/A')}")
        
        # Ejemplo de búsqueda híbrida
        print("\n🔍 Probando búsqueda híbrida...")
        try:
            # Buscar en documentos específicos
            results = await vector_store_service.search_by_document_ids(
                document_ids=[853346, 853347],
                query_text="Room 308",
                limit=5
            )
            print(f"✅ Búsqueda híbrida exitosa: {len(results)} resultados")
            
            if results:
                print("📋 Primeros resultados:")
                for i, result in enumerate(results[:3], 1):
                    print(f"   {i}. Score: {result['score']:.3f} - Doc: {result['metadata']['DocumentId']}")
                    print(f"      Texto: {result['text'][:100]}...")
                    
        except Exception as e:
            print(f"⚠️  No se pudo probar búsqueda: {e}")
        
    except Exception as e:
        logger.error(f"Error en procesamiento: {e}")
        print(f"❌ Error en procesamiento: {e}")
    finally:
        # Desconectar
        await vector_store_service.disconnect()
        print("\n✅ Procesamiento completado")

if __name__ == "__main__":
    asyncio.run(main()) 