"""
Script para probar los endpoints de la API REST.
"""
import asyncio
import httpx
import json

async def test_api_endpoints():
    """Prueba los endpoints de la API REST."""
    base_url = "http://localhost:8000/api/v1"
    
    print("🔍 Probando endpoints de la API REST...")
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Probar endpoint de estadísticas
            print("\n📊 1. Probando endpoint de estadísticas...")
            response = await client.get(f"{base_url}/vector-search/stats")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Estadísticas: {json.dumps(stats, indent=2)}")
            else:
                print(f"❌ Error: {response.text}")
            
            # 2. Probar búsqueda por similitud
            print("\n🔍 2. Probando búsqueda por similitud...")
            search_data = {
                "query_text": "room",
                "limit": 5,
                "score_threshold": 0.1
            }
            response = await client.post(
                f"{base_url}/vector-search/similarity",
                json=search_data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Resultados: {len(results['results'])}")
                for i, result in enumerate(results['results'][:3], 1):
                    print(f"   {i}. Score: {result['score']:.3f}")
                    print(f"      Doc: {result['document_id']}")
                    print(f"      Texto: {result['text'][:100]}...")
            else:
                print(f"❌ Error: {response.text}")
            
            # 3. Probar búsqueda híbrida
            print("\n🔍 3. Probando búsqueda híbrida...")
            hybrid_data = {
                "document_ids": [853346, 853347],
                "query_text": "room",
                "limit": 5
            }
            response = await client.post(
                f"{base_url}/vector-search/hybrid",
                json=hybrid_data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Resultados híbridos: {len(results['results'])}")
                for i, result in enumerate(results['results'][:3], 1):
                    print(f"   {i}. Score: {result['score']:.3f}")
                    print(f"      Doc: {result['document_id']}")
                    print(f"      Texto: {result['text'][:100]}...")
            else:
                print(f"❌ Error: {response.text}")
            
            # 4. Probar búsqueda por temperatura
            print("\n🔍 4. Probando búsqueda por temperatura...")
            temp_data = {
                "query_text": "temperature",
                "limit": 5,
                "score_threshold": 0.1
            }
            response = await client.post(
                f"{base_url}/vector-search/similarity",
                json=temp_data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Resultados: {len(results['results'])}")
                for i, result in enumerate(results['results'][:3], 1):
                    print(f"   {i}. Score: {result['score']:.3f}")
                    print(f"      Doc: {result['document_id']}")
                    print(f"      Texto: {result['text'][:100]}...")
            else:
                print(f"❌ Error: {response.text}")
            
            # 5. Probar búsqueda por crop
            print("\n🔍 5. Probando búsqueda por crop...")
            crop_data = {
                "query_text": "crop",
                "limit": 5,
                "score_threshold": 0.1
            }
            response = await client.post(
                f"{base_url}/vector-search/similarity",
                json=crop_data
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Resultados: {len(results['results'])}")
                for i, result in enumerate(results['results'][:3], 1):
                    print(f"   {i}. Score: {result['score']:.3f}")
                    print(f"      Doc: {result['document_id']}")
                    print(f"      Texto: {result['text'][:100]}...")
            else:
                print(f"❌ Error: {response.text}")
            
        except Exception as e:
            print(f"❌ Error en pruebas de API: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints()) 