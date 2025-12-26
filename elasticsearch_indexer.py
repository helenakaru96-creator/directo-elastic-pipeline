"""
Elasticsearch Indexer
Indexes financial data from Directo into Elasticsearch for flexible querying
"""

from elasticsearch import Elasticsearch, helpers
import pandas as pd
from typing import Dict, List
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElasticsearchIndexer:
    """Handles indexing of financial data into Elasticsearch"""
    
    def __init__(self, cloud_id: str = None, api_key: str = None, 
                 endpoint: str = None,
                 es_host: str = "localhost", es_port: int = 9200):
        """
        Initialize Elasticsearch connection (supports Cloud, Serverless, and local)
        
        Args:
            cloud_id: Elastic Cloud ID (for traditional deployments)
            api_key: Elastic API Key (for Cloud or Serverless)
            endpoint: Elasticsearch endpoint URL (for Serverless projects)
            es_host: Elasticsearch host (for local/Docker instances)
            es_port: Elasticsearch port (for local/Docker instances)
        """
        try:
            # PRIORITY 1: Serverless (endpoint-based)
            if endpoint and api_key:
                logger.info("🌐 Connecting to Elastic Serverless...")
                self.es = Elasticsearch(
                    endpoint,
                    api_key=api_key,
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                logger.info(f"✓ Connected to Elastic Serverless: {endpoint[:50]}...")
            
            # PRIORITY 2: Elastic Cloud (cloud_id-based)
            elif cloud_id and api_key:
                logger.info("🌐 Connecting to Elastic Cloud...")
                self.es = Elasticsearch(
                    cloud_id=cloud_id,
                    api_key=api_key,
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                logger.info(f"✓ Connected to Elastic Cloud (ID: {cloud_id[:30]}...)")
            
            # PRIORITY 3: Local Elasticsearch
            else:
                logger.info(f"🔧 Connecting to local Elasticsearch at {es_host}:{es_port}...")
                self.es = Elasticsearch(
                    [f"http://{es_host}:{es_port}"],
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                logger.info(f"✓ Connected to local Elasticsearch at {es_host}:{es_port}")
            
            # Verify connection
            if not self.es.ping():
                raise ConnectionError("Elasticsearch ping failed")
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Elasticsearch: {e}")
            raise
    
    def create_index_mappings(self):
        """Create index mappings for financial data"""
        
        # Invoice index mapping (based on actual Directo XML)
        invoice_mapping = {
            "mappings": {
                "properties": {
                    "number": {"type": "keyword"},
                    "date": {"type": "date"},
                    "duedate": {"type": "date"},
                    "transactiondate": {"type": "date"},
                    "vatzone": {"type": "keyword"},
                    "paymentterm": {"type": "keyword"},
                    "country": {"type": "keyword"},
                    "currency": {"type": "keyword"},
                    "currencyrate": {"type": "float"},
                    "customercode": {"type": "keyword"},
                    "customername": {"type": "text"},
                    "comment": {"type": "text"},
                    "address1": {"type": "text"},
                    "address2": {"type": "text"},
                    "address3": {"type": "text"},
                    "salesman": {"type": "keyword"},
                    "confirmed": {"type": "keyword"},
                    "netamount": {"type": "float"},
                    "vat": {"type": "float"},
                    "balance": {"type": "float"},
                    "totalamount": {"type": "float"},
                    "ts": {"type": "date"},
                    "indexed_at": {"type": "date"}
                }
            }
        }
        
        # Purchase index mapping (based on actual Directo XML)
        purchase_mapping = {
            "mappings": {
                "properties": {
                    "number": {"type": "keyword"},
                    "date": {"type": "date"},
                    "duedate": {"type": "date"},
                    "sum": {"type": "float"},
                    "supplierinvoiceno": {"type": "keyword"},
                    "paymentterm": {"type": "keyword"},
                    "supplier": {"type": "keyword"},
                    "suppliername": {"type": "text"},
                    "transactiontime": {"type": "date"},
                    "vat": {"type": "float"},
                    "asset": {"type": "keyword"},
                    "confirmed": {"type": "keyword"},
                    "ts": {"type": "date"},
                    "indexed_at": {"type": "date"}
                }
            }
        }
        
        # Item index mapping (based on actual Directo XML)
        item_mapping = {
            "mappings": {
                "properties": {
                    "code": {"type": "keyword"},
                    "name": {"type": "text"},
                    "class": {"type": "keyword"},
                    "class_name": {"type": "text"},
                    "unit": {"type": "keyword"},
                    "salesprice": {"type": "float"},
                    "vatprice": {"type": "float"},
                    "vatprice1": {"type": "float"},
                    "vatprice2": {"type": "float"},
                    "vatprice3": {"type": "float"},
                    "vatprice4": {"type": "float"},
                    "cost": {"type": "float"},
                    "closed": {"type": "keyword"},
                    "ts": {"type": "date"},
                    "tscreated": {"type": "date"},
                    "indexed_at": {"type": "date"}
                }
            }
        }
        
        # Project index mapping (based on actual Directo XML)
        project_mapping = {
            "mappings": {
                "properties": {
                    "code": {"type": "keyword"},
                    "name": {"type": "text"},
                    "manager": {"type": "keyword"},
                    "start": {"type": "date"},
                    "end": {"type": "date"},
                    "master": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "country": {"type": "keyword"},
                    "closed": {"type": "keyword"},
                    "points": {"type": "integer"},
                    "createdts": {"type": "date"},
                    "ts": {"type": "date"},
                    "indexed_at": {"type": "date"}
                }
            }
        }
        
        # Customer index mapping (based on actual Directo XML)
        customer_mapping = {
            "mappings": {
                "properties": {
                    "code": {"type": "keyword"},
                    "name": {"type": "text"},
                    "class": {"type": "keyword"},
                    "regno": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "salesman": {"type": "keyword"},
                    "country": {"type": "keyword"},
                    "email": {"type": "keyword"},
                    "address1": {"type": "text"},
                    "address2": {"type": "text"},
                    "ts": {"type": "date"},
                    "ts_created": {"type": "date"},
                    "indexed_at": {"type": "date"}
                }
            }
        }
        
        # Object index mapping (based on actual Directo XML)
        object_mapping = {
            "mappings": {
                "properties": {
                    "code": {"type": "keyword"},
                    "name": {"type": "text"},
                    "type": {"type": "keyword"},
                    "level": {"type": "keyword"},
                    "ts": {"type": "date"},
                    "indexed_at": {"type": "date"}
                }
            }
        }
        
        indices = {
            "invoices": invoice_mapping,
            "purchases": purchase_mapping,
            "items": item_mapping,
            "projects": project_mapping,
            "customers": customer_mapping,
            "objects": object_mapping
        }
        
        for index_name, mapping in indices.items():
            try:
                if self.es.indices.exists(index=index_name):
                    logger.info(f"Index '{index_name}' already exists")
                else:
                    self.es.indices.create(index=index_name, **mapping)
                    logger.info(f"Created index '{index_name}'")
            except Exception as e:
                logger.error(f"Error creating index '{index_name}': {e}")
                # Try to delete and recreate if it exists with wrong mapping
                try:
                    self.es.indices.delete(index=index_name, ignore=[400, 404])
                    self.es.indices.create(index=index_name, **mapping)
                    logger.info(f"Recreated index '{index_name}'")
                except Exception as e2:
                    logger.error(f"Failed to recreate index '{index_name}': {e2}")
    
    def index_dataframe(self, index_name: str, df: pd.DataFrame, id_field: str = None):
        """
        Index a pandas DataFrame into Elasticsearch
        
        Args:
            index_name: Name of the Elasticsearch index
            df: DataFrame to index
            id_field: Optional field to use as document ID
        """
        if df is None or df.empty:
            logger.warning(f"DataFrame for {index_name} is empty, skipping indexing")
            return 0
        
        logger.info(f"Preparing to index {len(df)} documents to '{index_name}'...")
        
        # Add indexing timestamp
        df = df.copy()  # Don't modify original
        df['indexed_at'] = datetime.now().isoformat()
        
        # Convert DataFrame to dictionary records
        records = df.to_dict('records')
        
        # Prepare bulk indexing actions
        actions = []
        for i, record in enumerate(records):
            # Clean up None values and convert to JSON-compatible types
            cleaned_record = {}
            for key, value in record.items():
                if pd.isna(value):
                    cleaned_record[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    cleaned_record[key] = value.isoformat() if not pd.isna(value) else None
                else:
                    cleaned_record[key] = value
            
            action = {
                "_index": index_name,
                "_source": cleaned_record
            }
            
            # Use specific field as document ID if provided
            if id_field and id_field in cleaned_record and cleaned_record[id_field]:
                action["_id"] = str(cleaned_record[id_field])
            
            actions.append(action)
        
        # Bulk index with error handling
        try:
            success, failed = helpers.bulk(
                self.es, 
                actions, 
                raise_on_error=False,
                chunk_size=500,
                request_timeout=60
            )
            
            logger.info(f"✓ Indexed {success} documents to '{index_name}'")
            
            if failed:
                logger.warning(f"⚠️  {len(failed)} documents failed to index")
                # Log first few failures for debugging
                for i, fail in enumerate(failed[:5]):
                    logger.error(f"  Failed doc {i+1}: {fail}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Bulk indexing failed for '{index_name}': {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def index_all_data(self, data: Dict[str, pd.DataFrame]):
        """
        Index all financial data from Directo
        
        Args:
            data: Dictionary of DataFrames from DirectoConnector
        """
        logger.info("Starting to index all financial data...")
        
        # Create indices if they don't exist
        self.create_index_mappings()
        
        # Index each dataset
        if 'invoices' in data:
            self.index_dataframe('invoices', data['invoices'], id_field='number')
        
        if 'purchases' in data:
            self.index_dataframe('purchases', data['purchases'], id_field='number')
        
        if 'items' in data:
            self.index_dataframe('items', data['items'], id_field='code')
        
        if 'projects' in data:
            self.index_dataframe('projects', data['projects'], id_field='code')
        
        if 'customers' in data:
            self.index_dataframe('customers', data['customers'], id_field='code')
        
        if 'objects' in data:
            self.index_dataframe('objects', data['objects'], id_field='code')
        
        if 'accounts' in data:
            self.index_dataframe('accounts', data['accounts'], id_field='code')
        
        if 'suppliers' in data:
            self.index_dataframe('suppliers', data['suppliers'], id_field='code')
        
        logger.info("All data indexed successfully")
    
    def search(self, index_name: str, query: dict):
        """
        Execute search query on Elasticsearch
        
        Args:
            index_name: Name of the index to search
            query: Elasticsearch query DSL
            
        Returns:
            Search results
        """
        result = self.es.search(index=index_name, **query)
        return result
    
    def aggregate(self, index_name: str, aggs: dict):
        """
        Execute aggregation query
        
        Args:
            index_name: Name of the index
            aggs: Aggregation query
            
        Returns:
            Aggregation results
        """
        query = {
            "size": 0,
            "aggs": aggs
        }
        result = self.es.search(index=index_name, **query)
        return result.get('aggregations', {})


if __name__ == "__main__":
    # Test the indexer
    indexer = ElasticsearchIndexer()
    indexer.create_index_mappings()
    
    print("Index mappings created successfully!")