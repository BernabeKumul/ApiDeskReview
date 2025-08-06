"""
Script para probar búsqueda híbrida con todos los fragmentos.
"""
import asyncio
import httpx
import json

async def test_hybrid_with_chunks():
    """Prueba la búsqueda híbrida con todos los fragmentos."""
    base_url = "http://localhost:8000/api/v1"
    
    print("🔍 Probando búsqueda híbrida con todos los fragmentos...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Probar búsqueda híbrida con la pregunta sobre pesticidas
            hybrid_data = {
                "document_ids": [853346, 853347, 853348, 853349, 853350],
                "query_text": "Question 9.01.03 pesticide risk assessment",
                "limit": 10
            }
            
            response = await client.post(
                f"{base_url}/vector-search/hybrid",
                json=hybrid_data
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Resultados híbridos: {len(results['results'])}")
                print(f"📄 Documentos con fragmentos: {len(results.get('all_chunks', {}))}")
                
                # Mostrar resultados de búsqueda
                for i, result in enumerate(results['results'][:3], 1):
                    print(f"\n🔍 Resultado {i}:")
                    print(f"   Score: {result['score']:.3f}")
                    print(f"   Doc: {result['document_id']}")
                    print(f"   Texto: {result['text'][:100]}...")
                
                # Mostrar todos los fragmentos de cada documento
                for doc_id, chunks in results.get('all_chunks', {}).items():
                    print(f"\n📄 Documento {doc_id} - Todos los fragmentos ({len(chunks)}):")
                    for j, chunk in enumerate(chunks[:5], 1):  # Mostrar solo los primeros 5
                        print(f"   Fragmento {j}: {chunk['text'][:80]}...")
                    if len(chunks) > 5:
                        print(f"   ... y {len(chunks) - 5} fragmentos más")
                
            else:
                print(f"❌ Error: {response.text}")
            
        except Exception as e:
            print(f"❌ Error en pruebas: {e}")

if __name__ == "__main__":
    asyncio.run(test_hybrid_with_chunks()) 