"""
Quick Elasticsearch Data Verification
Shows what data is currently indexed
"""

import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

def verify_indexed_data():
    """Check what data exists in Elasticsearch"""
    
    load_dotenv()
    
    endpoint = os.getenv("ELASTIC_ENDPOINT")
    api_key = os.getenv("ELASTIC_API_KEY")
    
    print("\n" + "="*70)
    print("ELASTICSEARCH DATA VERIFICATION")
    print("="*70)
    
    try:
        es = Elasticsearch(endpoint, api_key=api_key)
        
        if not es.ping():
            print("❌ Cannot connect to Elasticsearch")
            return
        
        print("✓ Connected to Elasticsearch")
        
        # List all indices
        indices = es.cat.indices(format='json')
        
        print("\n📊 INDEXED DATA:")
        print("-"*70)
        
        total_docs = 0
        index_data = []
        
        for idx in indices:
            index_name = idx['index']
            
            # Skip system indices
            if index_name.startswith('.'):
                continue
            
            doc_count = int(idx.get('docs.count', 0))
            size = idx.get('store.size', '0b')
            
            index_data.append({
                'name': index_name,
                'docs': doc_count,
                'size': size
            })
            
            total_docs += doc_count
        
        # Sort by document count (descending)
        index_data.sort(key=lambda x: x['docs'], reverse=True)
        
        # Display
        for data in index_data:
            print(f"  {data['name']:20s}  {data['docs']:>6,} docs  ({data['size']:>8})")
        
        print("-"*70)
        print(f"  {'TOTAL':20s}  {total_docs:>6,} docs")
        
        # Get sample invoice data
        if any(d['name'] == 'invoices' for d in index_data):
            print("\n📋 SAMPLE INVOICE DATA:")
            print("-"*70)
            
            result = es.search(
                index='invoices',
                body={
                    'size': 1,
                    'query': {'match_all': {}},
                    'sort': [{'transactiondate': {'order': 'desc'}}]
                }
            )
            
            if result['hits']['total']['value'] > 0:
                sample = result['hits']['hits'][0]['_source']
                print("Most recent invoice:")
                for key, value in sample.items():
                    if key != 'indexed_at':
                        print(f"  {key:20s}: {value}")
            
            # Get date range
            agg_result = es.search(
                index='invoices',
                body={
                    'size': 0,
                    'aggs': {
                        'min_date': {'min': {'field': 'transactiondate'}},
                        'max_date': {'max': {'field': 'transactiondate'}},
                        'total_amount': {'sum': {'field': 'total'}}
                    }
                }
            )
            
            aggs = agg_result['aggregations']
            invoice_count = result['hits']['total']['value']
            total = 0  # Initialize before use
            
            print("\n📈 INVOICE STATISTICS:")
            print("-"*70)
            
            if 'min_date' in aggs and aggs['min_date']['value']:
                from datetime import datetime
                min_date = datetime.fromtimestamp(aggs['min_date']['value'] / 1000)
                max_date = datetime.fromtimestamp(aggs['max_date']['value'] / 1000)
                
                print(f"  Date Range:     {min_date.strftime('%d.%m.%Y')} to {max_date.strftime('%d.%m.%Y')}")
            
            if 'total_amount' in aggs and aggs['total_amount']['value']:
                total = aggs['total_amount']['value']
                print(f"  Total Revenue:  €{total:,.2f}")
            
            if invoice_count > 0 and total > 0:
                avg = total / invoice_count
                print(f"  Average Value:  €{avg:,.2f}")
        
        print("\n" + "="*70)
        print("✅ DATA VERIFICATION COMPLETE")
        print("="*70)
        
        if total_docs > 0:
            print("\n🎉 You have data indexed! You can now:")
            print("  - Run queries: python main_openai.py → Option 2")
            print("  - Ask questions like:")
            print("    • 'What were total sales last year?'")
            print("    • 'Show me revenue by customer'")
            print("    • 'What's our average invoice value?'")
        else:
            print("\n⚠️  No data found. Run ETL pipeline:")
            print("  python main_openai.py → Option 1")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    verify_indexed_data()