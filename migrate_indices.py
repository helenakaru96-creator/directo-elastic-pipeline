"""
Migration Script for Elasticsearch Index Mapping Fix
Deletes old indices and recreates them with correct mappings
"""

import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

def migrate_indices():
    """Delete old indices and recreate with correct mappings"""
    
    load_dotenv()
    
    endpoint = os.getenv("ELASTIC_ENDPOINT")
    api_key = os.getenv("ELASTIC_API_KEY")
    
    print("\n" + "="*70)
    print("ELASTICSEARCH INDEX MIGRATION")
    print("="*70)
    
    if not endpoint or not api_key:
        print("\n❌ Missing ELASTIC_ENDPOINT or ELASTIC_API_KEY in .env")
        return False
    
    try:
        # Connect to Elasticsearch
        es = Elasticsearch(endpoint, api_key=api_key)
        
        if not es.ping():
            print("❌ Cannot connect to Elasticsearch")
            return False
        
        print("✓ Connected to Elasticsearch")
        
        # List of indices to migrate
        indices_to_migrate = [
            'invoices',
            'purchases',
            'items',
            'projects',
            'customers',
            'objects'
        ]
        
        print("\n⚠️  WARNING: This will DELETE existing indices and all their data!")
        print("Make sure you have backed up any important data.\n")
        
        confirm = input("Type 'YES' to continue with migration: ").strip()
        
        if confirm != 'YES':
            print("\n❌ Migration cancelled")
            return False
        
        print("\n📋 Starting migration...\n")
        
        # Delete old indices
        deleted_count = 0
        for index_name in indices_to_migrate:
            try:
                if es.indices.exists(index=index_name):
                    # Get document count before deletion
                    result = es.count(index=index_name)
                    doc_count = result['count']
                    
                    # Delete index
                    es.indices.delete(index=index_name)
                    print(f"✓ Deleted '{index_name}' ({doc_count:,} documents)")
                    deleted_count += 1
                else:
                    print(f"  '{index_name}' does not exist (skipping)")
            except Exception as e:
                print(f"❌ Error deleting '{index_name}': {e}")
        
        print(f"\n✓ Deleted {deleted_count} indices")
        
        # Create new indices with correct mappings
        print("\n📋 Creating new indices with corrected mappings...")
        
        from elasticsearch_indexer import ElasticsearchIndexer
        
        indexer = ElasticsearchIndexer(
            endpoint=endpoint,
            api_key=api_key
        )
        
        indexer.create_index_mappings()
        
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nNext steps:")
        print("1. Run ETL pipeline to re-index data:")
        print("   python main_openai.py → Option 1")
        print("\n2. Verify data was indexed correctly:")
        print("   python verify_data_quick.py")
        print("\n3. Test queries:")
        print("   python main_openai.py → Option 2")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    migrate_indices()
