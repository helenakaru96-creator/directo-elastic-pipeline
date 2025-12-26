"""
Directo API Connector
Handles data extraction from Directo accounting system
"""
import os
import requests
import pandas as pd
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DirectoConnector:
    """Connects to Directo API and extracts financial data"""
    
    def __init__(self, token: str):
        
        """
        Initialize Directo API connector
        
        Args:
            token: API token for authentication
        """
        self.base_url = "https://login.directo.ee/xmlcore/cap_bi/xmlcore.asp"
        self.token = token
        logger.info("DirectoConnector initialized")
    
    def _make_request(self, data_type: str, filters: Optional[Dict] = None) -> ET.Element:
        """
        Make request to Directo API
        
        Args:
            data_type: Type of data to fetch (invoice, customer, purchase, etc.)
            filters: Optional filters (ts, code, customercode, etc.)
            
        Returns:
            XML root element
        """
        params = {
            'token': self.token,
            'get': '1',
            'what': data_type
        }
        
        if filters:
            params.update(filters)
        
        try:
            response = requests.post(
                self.base_url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP Error: {response.status_code}")
            
            root = ET.fromstring(response.content)
            
            # Check for API errors
            if root.tag == 'err':
                raise Exception(f"API Error: {root.text}")
            elif root.tag == 'result' and root.get('type') == '5':
                raise Exception(f"Unauthorized: {root.get('desc')}")
            
            logger.info(f"Successfully fetched {data_type} data")
            return root
            
        except Exception as e:
            logger.error(f"Error fetching {data_type}: {e}")
            raise
    
    def _xml_to_dataframe(self, xml_root: ET.Element) -> pd.DataFrame:
        """Convert XML to pandas DataFrame"""
        data = []
        for element in xml_root:
            data.append(element.attrib)
        return pd.DataFrame(data)
    
    def get_invoices(self, from_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch invoices (sales data)
        
        Args:
            from_date: Optional start date in DD.MM.YYYY format
            
        Returns:
            DataFrame with invoice data
        """
        filters = {}
        if from_date:
            filters['ts'] = from_date
        
        xml_data = self._make_request('invoice', filters)
        df = self._xml_to_dataframe(xml_data)
        
        if not df.empty:
            # Convert data types
            if 'transactiondate' in df.columns:
                df['transactiondate'] = pd.to_datetime(df['transactiondate'], errors='coerce')
            
            # Convert numeric fields
            numeric_fields = ['number']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
        
        logger.info(f"Retrieved {len(df)} invoices")
        return df
    
    def get_customers(self, from_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch customer data"""
        filters = {}
        if from_date:
            filters['ts'] = from_date
        
        xml_data = self._make_request('customer', filters)
        df = self._xml_to_dataframe(xml_data)
        logger.info(f"Retrieved {len(df)} customers")
        return df
    
    def get_purchases(self, from_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch purchase data (costs)"""
        filters = {}
        if from_date:
            filters['ts'] = from_date
        
        xml_data = self._make_request('purchase', filters)
        df = self._xml_to_dataframe(xml_data)
        
        if not df.empty and 'date1' in df.columns:
            df['date1'] = pd.to_datetime(df['date1'], errors='coerce')
        
        logger.info(f"Retrieved {len(df)} purchases")
        return df
    
    def get_items(self, from_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch items/products"""
        filters = {}
        if from_date:
            filters['ts'] = from_date
        
        xml_data = self._make_request('item', filters)
        df = self._xml_to_dataframe(xml_data)
        logger.info(f"Retrieved {len(df)} items")
        return df
    
    def get_projects(self, from_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch projects"""
        filters = {}
        if from_date:
            filters['ts'] = from_date
        
        xml_data = self._make_request('project', filters)
        df = self._xml_to_dataframe(xml_data)
        logger.info(f"Retrieved {len(df)} projects")
        return df
    
    def get_objects(self, from_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch objects (organizational structure)"""
        filters = {}
        if from_date:
            filters['ts'] = from_date
        
        xml_data = self._make_request('object', filters)
        df = self._xml_to_dataframe(xml_data)
        logger.info(f"Retrieved {len(df)} objects")
        return df
    
    def get_accounts(self, from_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch accounts"""
        filters = {}
        if from_date:
            filters['ts'] = from_date
        
        xml_data = self._make_request('account', filters)
        df = self._xml_to_dataframe(xml_data)
        logger.info(f"Retrieved {len(df)} accounts")
        return df
    
    def get_suppliers(self, from_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch suppliers"""
        filters = {}
        if from_date:
            filters['ts'] = from_date
        
        xml_data = self._make_request('supplier', filters)
        df = self._xml_to_dataframe(xml_data)
        logger.info(f"Retrieved {len(df)} suppliers")
        return df
    
    def get_all_financial_data(self, from_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch all financial data needed for analysis
        
        Returns:
            Dictionary of DataFrames with all financial data
        """
        logger.info("Fetching all financial data from Directo...")
        
        data = {
            'invoices': self.get_invoices(from_date),
            'customers': self.get_customers(from_date),
            'purchases': self.get_purchases(from_date),
            'items': self.get_items(from_date),
            'projects': self.get_projects(from_date),
            'objects': self.get_objects(from_date),
            'accounts': self.get_accounts(from_date),
            'suppliers': self.get_suppliers(from_date)
        }
        
        logger.info("All financial data fetched successfully")
        return data


if __name__ == "__main__":
    
    # Test the connector
    TOKEN = "directo_api_token_here"
    
    connector = DirectoConnector(TOKEN)
    
    # Fetch data from last 6 months
    from_date = (datetime.now() - timedelta(days=180)).strftime("%d.%m.%Y")
    
    data = connector.get_all_financial_data(from_date)
    
    for name, df in data.items():
        print(f"\n{name}: {len(df)} records")
        if not df.empty:
            print(df.head())