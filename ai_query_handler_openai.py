"""
AI Query Handler - OpenAI ChatGPT Version
Handles natural language queries using ChatGPT and Elasticsearch
"""

from openai import OpenAI
from elasticsearch import Elasticsearch
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIQueryHandler:
    """Handles AI-powered queries on financial data using ChatGPT"""
    
    def __init__(self, openai_api_key: str, 
                 elastic_endpoint: str = None,
                 elastic_cloud_id: str = None,
                 elastic_api_key: str = None,
                 es_host: str = "localhost", 
                 es_port: int = 9200):
        """
        Initialize AI Query Handler with OpenAI and Elasticsearch
        
        Args:
            openai_api_key: OpenAI API key
            elastic_endpoint: Elasticsearch endpoint URL (for Serverless - takes priority)
            elastic_cloud_id: Elastic Cloud ID (for traditional deployments)
            elastic_api_key: Elastic API Key (for Cloud or Serverless)
            es_host: Elasticsearch host (for local instances)
            es_port: Elasticsearch port (for local instances)
        """
        self.client = OpenAI(api_key=openai_api_key)
        
        # Initialize Elasticsearch - Priority: Serverless > Cloud > Local
        try:
            if elastic_endpoint and elastic_api_key:
                logger.info("🌐 AI Handler connecting to Elastic Serverless...")
                self.es = Elasticsearch(
                    elastic_endpoint,
                    api_key=elastic_api_key,
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                logger.info("✓ AI Handler connected to Elastic Serverless")
            elif elastic_cloud_id and elastic_api_key:
                logger.info("🌐 AI Handler connecting to Elastic Cloud...")
                self.es = Elasticsearch(
                    cloud_id=elastic_cloud_id,
                    api_key=elastic_api_key,
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                logger.info("✓ AI Handler connected to Elastic Cloud")
            else:
                logger.info(f"🔧 AI Handler connecting to local Elasticsearch...")
                self.es = Elasticsearch(
                    [f"http://{es_host}:{es_port}"],
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                logger.info(f"✓ AI Handler connected to local Elasticsearch")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise
        
        logger.info("AI Query Handler initialized with ChatGPT")
    
    def _build_elasticsearch_query(self, user_question: str) -> Dict:
        """
        Use ChatGPT to convert natural language to Elasticsearch query
        
        Args:
            user_question: User's question in natural language
            
        Returns:
            Elasticsearch query dictionary
        """
        prompt = f"""You are a financial data analyst. Convert this natural language question into an Elasticsearch query.

Available indices and their fields:
- invoices: number, date, duedate, transactiondate, vatzone, paymentterm, country, currency, currencyrate, customercode, customername, comment, address1, address2, address3, salesman, confirmed, netamount, vat, balance, totalamount, ts
- purchases: number, date, duedate, sum, supplierinvoiceno, paymentterm, supplier, suppliername, transactiontime, vat, asset, confirmed, ts
- items: code, name, class, class_name, unit, salesprice, vatprice, vatprice1, vatprice2, vatprice3, vatprice4, cost, closed, ts, tscreated
- projects: code, name, manager, start, end, master, type, country, closed, points, createdts, ts
- customers: code, name, class, regno, type, salesman, country, email, address1, address2, ts, ts_created
- objects: code, name, type, level, ts

User question: {user_question}

Generate an Elasticsearch query DSL in JSON format. Include:
1. The index/indices to search
2. Filters for specific criteria (country, salesman, project, etc.)
3. Aggregations if the question asks for sums, averages, or groupings
4. Date ranges if mentioned (use transactiondate for invoices, date for purchases)

Return ONLY valid JSON with this structure:
{{
    "indices": ["index_name"],
    "query": {{ ... }},
    "aggs": {{ ... }} (optional)
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o (optimized) or use "gpt-4-turbo" or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a data analyst expert in Elasticsearch queries. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent query generation
            max_tokens=2000
        )
        
        # Extract JSON from ChatGPT's response
        response_text = response.choices[0].message.content
        
        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            query_spec = json.loads(response_text)
            logger.info(f"Generated Elasticsearch query: {json.dumps(query_spec, indent=2)}")
            return query_spec
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ChatGPT response as JSON: {e}")
            logger.error(f"Response: {response_text}")
            raise
    
    def _execute_elasticsearch_query(self, query_spec: Dict) -> Dict:
        """
        Execute Elasticsearch query
        
        Args:
            query_spec: Query specification from ChatGPT
            
        Returns:
            Query results
        """
        indices = query_spec.get('indices', ['invoices'])
        query = query_spec.get('query', {"match_all": {}})
        aggs = query_spec.get('aggs', {})
        
        # Build Elasticsearch query body
        body = {"query": query}
        if aggs:
            body["aggs"] = aggs
            body["size"] = 0  # Don't return documents, only aggregations
        else:
            body["size"] = 100  # Return up to 100 documents
        
        # Execute query
        result = self.es.search(index=','.join(indices), **body)
        logger.info(f"Elasticsearch query returned {result['hits']['total']['value']} hits")
        
        return result
    
    def _format_results_for_ai(self, es_results: Dict) -> str:
        """
        Format Elasticsearch results for AI analysis
        
        Args:
            es_results: Results from Elasticsearch
            
        Returns:
            Formatted string for AI
        """
        formatted = []
        
        # Format aggregations
        if 'aggregations' in es_results:
            formatted.append("Aggregation Results:")
            formatted.append(json.dumps(es_results['aggregations'], indent=2))
        
        # Format document hits
        if 'hits' in es_results and es_results['hits']['total']['value'] > 0:
            formatted.append(f"\nDocument Hits ({es_results['hits']['total']['value']} total):")
            for hit in es_results['hits']['hits'][:20]:  # First 20 documents
                formatted.append(json.dumps(hit['_source'], indent=2))
        
        return "\n".join(formatted)
    
    def answer_question(self, user_question: str) -> str:
        """
        Answer user's question using AI and financial data
        
        Args:
            user_question: User's natural language question
            
        Returns:
            AI-generated answer
        """
        logger.info(f"Processing question: {user_question}")
        
        try:
            # Step 1: Convert question to Elasticsearch query using AI
            query_spec = self._build_elasticsearch_query(user_question)
            
            # Step 2: Execute query on Elasticsearch
            es_results = self._execute_elasticsearch_query(query_spec)
            
            # Step 3: Format results
            formatted_results = self._format_results_for_ai(es_results)
            
            # Step 4: Use AI to analyze results and generate answer
            analysis_prompt = f"""You are a financial analyst AI assistant. Based on the following financial data retrieved from the company's accounting system, answer the user's question.

User Question: {user_question}

Financial Data Retrieved:
{formatted_results}

Provide a comprehensive answer that:
1. Directly answers the question
2. Includes specific numbers and metrics
3. Provides insights and analysis
4. If asked for forecasts, use historical data patterns to make reasonable predictions
5. Mentions any assumptions or limitations

Answer in a professional but conversational tone."""

            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o for best reasoning
                messages=[
                    {"role": "system", "content": "You are a professional financial analyst with expertise in data analysis and forecasting."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,  # Balanced creativity and consistency
                max_tokens=4000
            )
            
            answer = response.choices[0].message.content
            logger.info("Answer generated successfully")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return f"I encountered an error processing your question: {str(e)}. Please try rephrasing your question or check if the data is available in the system."
    
    def forecast_financial_metrics(self, metric: str, periods: int = 6) -> str:
        """
        Generate financial forecast using historical data
        
        Args:
            metric: Metric to forecast (revenue, costs, profit, etc.)
            periods: Number of periods to forecast
            
        Returns:
            Forecast analysis
        """
        # Query historical data
        query = {
            "indices": ["invoices", "purchases"],
            "query": {
                "range": {
                    "transactiondate": {
                        "gte": "now-2y"
                    }
                }
            },
            "aggs": {
                "monthly_revenue": {
                    "date_histogram": {
                        "field": "transactiondate",
                        "calendar_interval": "month"
                    },
                    "aggs": {
                        "total_amount": {
                            "sum": {
                                "field": "amount"
                            }
                        }
                    }
                }
            }
        }
        
        es_results = self._execute_elasticsearch_query(query)
        formatted_results = self._format_results_for_ai(es_results)
        
        forecast_prompt = f"""You are a financial forecasting expert. Based on the historical financial data below, forecast the {metric} for the next {periods} months.

Historical Data:
{formatted_results}

Provide:
1. Monthly forecast for the next {periods} months
2. Methodology used (trend analysis, seasonality, etc.)
3. Confidence intervals or ranges
4. Key assumptions
5. Risk factors to consider

Present the forecast in a clear, structured format with specific numbers."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial forecasting expert specializing in time series analysis and predictive modeling."},
                {"role": "user", "content": forecast_prompt}
            ],
            temperature=0.5,  # Lower temperature for more consistent forecasts
            max_tokens=4000
        )
        
        return response.choices[0].message.content


if __name__ == "__main__":
    # Test the AI Query Handler
    import os
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
    
    handler = AIQueryHandler(OPENAI_API_KEY)
    
    # Test query
    question = "What were our total sales in the Netherlands last quarter?"
    answer = handler.answer_question(question)
    print(f"\nQuestion: {question}")
    print(f"\nAnswer: {answer}")