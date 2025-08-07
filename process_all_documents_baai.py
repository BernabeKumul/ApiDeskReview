"""
Script para procesar TODOS los documentos del JSON con el modelo BAAI/bge-m3.
Evita duplicados automáticamente.
"""
import asyncio
import logging
from app.services.baai_document_processor import baai_document_processor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_all_documents():
    """Procesa todos los documentos del JSON con BAAI/bge-m3."""
    
    print("🚀 Iniciando procesamiento de TODOS los documentos con BAAI/bge-m3...")
    print("📄 Leyendo documentos desde JSON/AzzuleAI.AIDocuments.json")
    print("🔍 Verificando duplicados automáticamente...")
    print("⚡ Usando modelo BAAI/bge-m3 (1024 dimensiones)")
    print("=" * 80)
    
    try:
        # Procesar todos los documentos sin límite
        result = await baai_document_processor.process_all_documents(limit=None)
        
        print("\n" + "=" * 80)
        print("📊 RESULTADOS DEL PROCESAMIENTO:")
        print("=" * 80)
        print(f"✅ Éxito: {result['success']}")
        print(f"📝 Mensaje: {result['message']}")
        print(f"🔄 Documentos procesados: {result['processed']}")
        print(f"⏭️  Documentos saltados (duplicados): {result['skipped']}")
        print(f"❌ Errores: {result['errors']}")
        print(f"📊 Total de documentos en JSON: {result['total_documents']}")
        
        if result.get('collection_stats'):
            stats = result['collection_stats']
            print(f"\n📈 ESTADÍSTICAS DE LA COLECCIÓN:")
            print(f"   - Nombre: {stats.get('collection_name', 'N/A')}")
            print(f"   - Puntos en la colección: {stats.get('points_count', 0)}")
            print(f"   - Tamaño del vector: {stats.get('vector_size', 0)}")
            print(f"   - Segmentos: {stats.get('segments_count', 0)}")
            print(f"   - Estado: {stats.get('status', 'N/A')}")
        
        # Calcular porcentajes
        total = result['processed'] + result['skipped'] + result['errors']
        if total > 0:
            processed_pct = (result['processed'] / total) * 100
            skipped_pct = (result['skipped'] / total) * 100
            error_pct = (result['errors'] / total) * 100
            
            print(f"\n📊 PORCENTAJES:")
            print(f"   - Procesados: {processed_pct:.1f}%")
            print(f"   - Saltados: {skipped_pct:.1f}%")
            print(f"   - Errores: {error_pct:.1f}%")
        
        if result['success']:
            print("\n🎉 ¡PROCESAMIENTO COMPLETADO EXITOSAMENTE!")
            print(f"✅ Se procesaron {result['processed']} documentos nuevos")
            if result['skipped'] > 0:
                print(f"⏭️  Se saltaron {result['skipped']} documentos duplicados")
        else:
            print("\n❌ ERROR EN EL PROCESAMIENTO")
            print(f"💬 {result['message']}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        logger.error(f"Error en procesamiento masivo: {e}")
        return {
            "success": False,
            "message": f"Error crítico: {str(e)}",
            "processed": 0,
            "skipped": 0,
            "errors": 1
        }

if __name__ == "__main__":
    print("🧪 Iniciando procesamiento masivo de documentos con BAAI/bge-m3...")
    print("⚠️  Este proceso puede tomar varios minutos...")
    print("💾 El modelo BAAI/bge-m3 se descargará automáticamente si es necesario")
    print()
    
    # Ejecutar procesamiento
    result = asyncio.run(process_all_documents())
    
    print("\n🏁 Proceso finalizado!")
    if result['success']:
        print("✅ Todos los documentos han sido procesados exitosamente")
    else:
        print("❌ Hubo errores durante el procesamiento") 