"""
Web Interface for Financial AI Assistant (OpenAI Version)
Simple Flask application with chat interface powered by ChatGPT
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from main_openai import FinancialAIAssistant
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize assistant
from dotenv import load_dotenv
load_dotenv()

DIRECTO_TOKEN = os.getenv("DIRECTO_TOKEN", "your_directo_token_here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# Elasticsearch (priority: Serverless > Cloud > Local)
ELASTIC_ENDPOINT = os.getenv("ELASTIC_ENDPOINT")
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

# Local Elasticsearch (fallback)
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = int(os.getenv("ES_PORT", "9200"))

assistant = FinancialAIAssistant(
    directo_token=DIRECTO_TOKEN,
    openai_api_key=OPENAI_API_KEY,
    elastic_endpoint=ELASTIC_ENDPOINT,
    elastic_cloud_id=ELASTIC_CLOUD_ID,
    elastic_api_key=ELASTIC_API_KEY,
    es_host=ES_HOST,
    es_port=ES_PORT
)

# Simple HTML template for chat interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Financial AI Assistant (ChatGPT)</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            height: 600px;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 20px 20px 0 0;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
            color: white;
        }
        
        .message.assistant .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        
        .input-container {
            padding: 20px;
            background: white;
            border-radius: 0 0 20px 20px;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
        }
        
        #questionInput {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        #questionInput:focus {
            border-color: #10a37f;
        }
        
        #sendButton {
            padding: 12px 30px;
            background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        #sendButton:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(16, 163, 127, 0.4);
        }
        
        #sendButton:active {
            transform: translateY(0);
        }
        
        #sendButton:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #666;
            font-style: italic;
        }
        
        .examples {
            padding: 10px 0;
            font-size: 12px;
            color: #666;
        }
        
        .example-query {
            display: inline-block;
            background: #f0f0f0;
            padding: 5px 10px;
            margin: 3px;
            border-radius: 12px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .example-query:hover {
            background: #e0e0e0;
        }
        
        .powered-by {
            text-align: center;
            padding: 5px;
            font-size: 11px;
            color: white;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💼 Financial AI Assistant</h1>
            <p>Ask questions about your company's financial data</p>
            <div class="powered-by">Powered by ChatGPT-4</div>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message assistant">
                <div class="message-content">
                    Hello! I'm your Financial AI Assistant powered by ChatGPT. I can help you analyze your company's financial data from Directo.
                    <br><br>
                    <strong>Try asking:</strong>
                    <div class="examples">
                        <span class="example-query" onclick="askExample(this)">What were our total sales in the Netherlands last quarter?</span>
                        <span class="example-query" onclick="askExample(this)">Forecast our revenue for the next 6 months</span>
                        <span class="example-query" onclick="askExample(this)">Which salesperson had the highest sales?</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="loading" id="loading">Analyzing your question with ChatGPT...</div>
        
        <div class="input-container">
            <div class="input-group">
                <input 
                    type="text" 
                    id="questionInput" 
                    placeholder="Ask a question about your financial data..." 
                    onkeypress="handleKeyPress(event)"
                />
                <button id="sendButton" onclick="sendQuestion()">Send</button>
            </div>
        </div>
    </div>

    <script>
        function addMessage(content, isUser) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        async function sendQuestion() {
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            
            if (!question) return;
            
            // Add user message
            addMessage(question, true);
            input.value = '';
            
            // Show loading
            const loading = document.getElementById('loading');
            const sendButton = document.getElementById('sendButton');
            loading.style.display = 'block';
            sendButton.disabled = true;
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                
                // Add assistant response
                addMessage(data.answer, false);
                
            } catch (error) {
                addMessage('Sorry, I encountered an error processing your question. Please try again.', false);
                console.error('Error:', error);
            } finally {
                loading.style.display = 'none';
                sendButton.disabled = false;
                input.focus();
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendQuestion();
            }
        }
        
        function askExample(element) {
            const question = element.textContent;
            document.getElementById('questionInput').value = question;
            sendQuestion();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the chat interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """API endpoint to answer questions"""
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        logger.info(f"Received question: {question}")
        
        # Get answer from AI assistant
        answer = assistant.answer_question(question)
        
        return jsonify({'answer': answer})
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/etl', methods=['POST'])
def run_etl():
    """API endpoint to trigger ETL pipeline"""
    try:
        data = request.json
        from_date = data.get('from_date', None)
        
        logger.info("ETL pipeline triggered via API")
        success = assistant.run_etl_pipeline(from_date)
        
        if success:
            return jsonify({'status': 'success', 'message': 'ETL pipeline completed successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'ETL pipeline failed'}), 500
            
    except Exception as e:
        logger.error(f"Error running ETL: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'ai_provider': 'OpenAI ChatGPT'})


if __name__ == '__main__':
    print("\n" + "="*70)
    print("Financial AI Assistant - Web Interface (Powered by ChatGPT)")
    print("="*70)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)