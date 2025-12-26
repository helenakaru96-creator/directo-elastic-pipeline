"""
Financial AI Assistant - Main Application (OpenAI Version)
Integrates Directo, Elasticsearch, and ChatGPT for financial analysis and forecasting
"""

import os
from datetime import datetime, timedelta
from typing import Dict
import logging
import schedule
import time

from directo_connector import DirectoConnector
from elasticsearch_indexer import ElasticsearchIndexer
from ai_query_handler_openai import AIQueryHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinancialAIAssistant:
    """Main application class for Financial AI Assistant (OpenAI Version)"""
    
    def __init__(
        self,
        directo_token: str,
        openai_api_key: str,
        elastic_endpoint: str = None,
        elastic_cloud_id: str = None,
        elastic_api_key: str = None,
        es_host: str = "localhost",
        es_port: int = 9200
    ):
        """
        Initialize Financial AI Assistant
        
        Args:
            directo_token: Directo API token
            openai_api_key: OpenAI API key
            elastic_endpoint: Elasticsearch endpoint URL (for Serverless - takes priority)
            elastic_cloud_id: Elastic Cloud ID (for traditional Cloud deployments)
            elastic_api_key: Elastic API Key (for Cloud or Serverless)
            es_host: Elasticsearch host (for local instances)
            es_port: Elasticsearch port (for local instances)
        """
        self.directo = DirectoConnector(directo_token)
        self.indexer = ElasticsearchIndexer(
            endpoint=elastic_endpoint,
            cloud_id=elastic_cloud_id,
            api_key=elastic_api_key,
            es_host=es_host,
            es_port=es_port
        )
        self.ai_handler = AIQueryHandler(
            openai_api_key=openai_api_key,
            elastic_endpoint=elastic_endpoint,
            elastic_cloud_id=elastic_cloud_id,
            elastic_api_key=elastic_api_key,
            es_host=es_host,
            es_port=es_port
        )
        
        logger.info("Financial AI Assistant initialized with ChatGPT and Elasticsearch")
    
    def run_etl_pipeline(self, from_date: str = None):
        """
        Run ETL pipeline: Extract from Directo, Transform, Load to Elasticsearch
        
        Args:
            from_date: Optional start date in DD.MM.YYYY format
        """
        logger.info("Starting ETL pipeline...")
        
        try:
            # Extract data from Directo
            logger.info("Step 1: Extracting data from Directo...")
            if not from_date:
                # Default to last 10 years (to capture all historical data)
                from_date = (datetime.now() - timedelta(days=3650)).strftime("%d.%m.%Y")
                logger.info(f"Using default date range: from {from_date} to today")
            else:
                logger.info(f"Using specified date range: from {from_date} to today")
            
            data = self.directo.get_all_financial_data(from_date)
            
            # Log data summary
            for name, df in data.items():
                logger.info(f"Extracted {len(df)} {name}")
            
            # Transform and Load to Elasticsearch
            logger.info("Step 2: Loading data to Elasticsearch...")
            self.indexer.index_all_data(data)
            
            logger.info("ETL pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            return False
    
    def interactive_chat(self):
        """Run interactive chat interface"""
        print("\n" + "="*70)
        print("Financial AI Assistant - Interactive Mode (Powered by ChatGPT)")
        print("="*70)
        print("\nAsk me anything about your company's financial data!")
        print("Examples:")
        print("  - How much did we sell in the Netherlands last quarter?")
        print("  - What is the profitability of product X in country Y?")
        print("  - Forecast our revenue for the next 6 months")
        print("  - Which salesperson had the highest sales in Q3?")
        print("\nType 'exit' to quit\n")
        
        while True:
            try:
                question = input("\nYour question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                print("\nAnalyzing... (this may take a moment)")
                
                # Get answer from AI
                answer = self.ai_handler.answer_question(question)
                
                print("\n" + "-"*70)
                print("Answer:")
                print("-"*70)
                print(answer)
                print("-"*70)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\nError: {e}")
    
    def answer_question(self, question: str) -> str:
        """
        Answer a single question (for API/web interface)
        
        Args:
            question: User's question
            
        Returns:
            AI-generated answer
        """
        return self.ai_handler.answer_question(question)
    
    def schedule_daily_etl(self, time_str: str = "02:00"):
        """
        Schedule daily ETL pipeline run
        
        Args:
            time_str: Time to run ETL (e.g., "02:00")
        """
        logger.info(f"Scheduling daily ETL at {time_str}")
        schedule.every().day.at(time_str).do(self.run_etl_pipeline)
        
        print(f"ETL pipeline scheduled to run daily at {time_str}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nScheduler stopped")


def main():
    """Main entry point"""
    
    # Load from .env file if available
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configuration - Loads from .env or environment variables
    DIRECTO_TOKEN = os.getenv("DIRECTO_TOKEN", "your_directo_token_here")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    # Elasticsearch configuration (priority order: Serverless > Cloud > Local)
    ELASTIC_ENDPOINT = os.getenv("ELASTIC_ENDPOINT")      # Serverless
    ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")      # Traditional Cloud
    ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")        # Both Serverless & Cloud
    
    # Local Elasticsearch (fallback)
    ES_HOST = os.getenv("ES_HOST", "localhost")
    ES_PORT = int(os.getenv("ES_PORT", "9200"))
    
    # Initialize assistant
    assistant = FinancialAIAssistant(
        directo_token=DIRECTO_TOKEN,
        openai_api_key=OPENAI_API_KEY,
        elastic_endpoint=ELASTIC_ENDPOINT,
        elastic_cloud_id=ELASTIC_CLOUD_ID,
        elastic_api_key=ELASTIC_API_KEY,
        es_host=ES_HOST,
        es_port=ES_PORT
    )
    
    # Menu
    print("\n" + "="*70)
    print("Financial AI Assistant (Powered by ChatGPT)")
    print("="*70)
    print("\n1. Run ETL Pipeline (fetch and index data)")
    print("2. Start Interactive Chat")
    print("3. Answer Single Question")
    print("4. Schedule Daily ETL")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        print("\n💡 Date Options:")
        print("   - Press Enter: Last 10 years (recommended for complete data)")
        print("   - Or enter specific date (DD.MM.YYYY), e.g., 01.01.2014")
        from_date = input("\nFrom date: ").strip()
        assistant.run_etl_pipeline(from_date if from_date else None)
    
    elif choice == "2":
        # Run ETL first if needed
        confirm = input("\nRun ETL pipeline first? (y/n): ").strip().lower()
        if confirm == 'y':
            assistant.run_etl_pipeline()
        assistant.interactive_chat()
    
    elif choice == "3":
        question = input("\nYour question: ").strip()
        if question:
            print("\nAnalyzing...")
            answer = assistant.answer_question(question)
            print("\n" + "="*70)
            print("Answer:")
            print("="*70)
            print(answer)
    
    elif choice == "4":
        time_str = input("\nTime to run daily ETL (HH:MM, default 02:00): ").strip()
        if not time_str:
            time_str = "02:00"
        assistant.schedule_daily_etl(time_str)
    
    else:
        print("Goodbye!")


if __name__ == "__main__":
    main()