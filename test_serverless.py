"""
Elastic Serverless Connection Test
For Serverless Elasticsearch projects (not traditional deployments)
"""

import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

def test_serverless_connection():
    """Test connection to Elastic Serverless"""
    
    load_dotenv()
    
    print("\n" + "="*70)
    print("ELASTIC SERVERLESS CONNECTION TEST")
    print("="*70)
    
    # Serverless uses endpoint URL instead of cloud_id
    endpoint = os.getenv("ELASTIC_ENDPOINT")
    api_key = os.getenv("ELASTIC_API_KEY")
    
    print("\n📋 Configuration Check:")
    
    if not endpoint:
        print("\n❌ ELASTIC_ENDPOINT not found in .env")
        print("\n📝 HOW TO GET SERVERLESS ENDPOINT:")
        print("   1. Go to: https://cloud.elastic.co/projects")
        print("   2. Click on your Serverless project")
        print("   3. Go to 'Elasticsearch' section")
        print("   4. Copy the 'Endpoint' URL")
        print("   5. It should look like:")
        print("      https://your-project.es.us-central1.gcp.elastic-cloud.com")
        print("\n   Add to .env:")
        print("   ELASTIC_ENDPOINT=https://your-project.es.region.gcp.elastic-cloud.com")
        return False
    
    if not api_key:
        print("\n❌ ELASTIC_API_KEY not found in .env")
        print("\n📝 HOW TO CREATE SERVERLESS API KEY:")
        print("   1. In your Serverless project")
        print("   2. Go to 'Management' > 'API Keys'")
        print("   3. Click 'Create API Key'")
        print("   4. Copy the generated key")
        print("\n   Add to .env:")
        print("   ELASTIC_API_KEY=your_api_key_here")
        return False
    
    print(f"✓ Endpoint found: {endpoint}")
    print(f"✓ API Key found: {api_key[:20]}...")
    
    # Test connection
    print("\n🌐 Connecting to Elastic Serverless...")
    
    try:
        # Serverless connection
        es = Elasticsearch(
            endpoint,
            api_key=api_key,
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
        
        print("✓ Client created")
        
        # Test ping
        if not es.ping():
            print("❌ Ping failed")
            return False
        
        print("✓ Ping successful!")
        
        # Get cluster info
        info = es.info()
        print("\n" + "="*70)
        print("CLUSTER INFORMATION")
        print("="*70)
        print(f"Cluster Name: {info.get('cluster_name', 'N/A')}")
        print(f"Version: {info['version']['number']}")
        print(f"Tagline: {info.get('tagline', 'N/A')}")
        
        # List indices
        print("\n" + "="*70)
        print("INDICES")
        print("="*70)
        
        try:
            indices = es.cat.indices(format='json')
            if indices:
                print(f"\nFound {len(indices)} indices:")
                for idx in indices:
                    print(f"  - {idx['index']}: {idx.get('docs.count', '0')} documents")
            else:
                print("No indices found (empty database)")
        except Exception as e:
            print(f"Note: Could not list indices (might need permissions): {e}")
        
        print("\n" + "="*70)
        print("✅ SERVERLESS CONNECTION SUCCESSFUL!")
        print("="*70)
        print("\nYou can now run the ETL pipeline:")
        print("  python main_openai.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        print("\n🔧 TROUBLESHOOTING:")
        print("\n1. Verify Endpoint URL:")
        print("   - Should start with https://")
        print("   - Should NOT have trailing slash")
        print("   - Example: https://my-project.es.us-central1.gcp.elastic-cloud.com")
        
        print("\n2. Verify API Key:")
        print("   - Create new API key in Serverless project")
        print("   - Ensure it has proper permissions")
        print("   - Copy the ENCODED key (not decoded)")
        
        print("\n3. Check Project Status:")
        print("   - Ensure Serverless project is active")
        print("   - Check if Elasticsearch is enabled")
        
        return False


if __name__ == "__main__":
    test_serverless_connection()