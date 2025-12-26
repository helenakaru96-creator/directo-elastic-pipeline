# Financial AI Assistant - User Guide

**Version 1.0 - ChatGPT Powered**

---

## Table of Contents
1. [System Overview](#system-overview)
2. [First-Time Setup](#first-time-setup)
3. [Daily Usage](#daily-usage)
4. [Troubleshooting](#troubleshooting)
5. [Example Questions](#example-questions)
6. [Understanding Results](#understanding-results)

---

## System Overview

### What Does This System Do?

The Financial AI Assistant solves a critical business problem: **Directo's reporting limitations for multi-dimensional analysis**.

**Problem:** In Directo, it's nearly impossible to get reports like:
- "Sales of product X in the Netherlands by each salesperson across all projects"
- "Profitability analysis by country, region, and item class"
- Complex forecasting based on historical patterns

**Solution:** This system:
1. **Extracts** data from Directo (invoices, customers, purchases, etc.)
2. **Indexes** it in Elasticsearch (enables flexible multi-dimensional queries)
3. **Uses ChatGPT-4** to understand your questions and provide intelligent analysis

### Architecture

```
┌─────────────┐     ETL Pipeline      ┌──────────────────┐
│   Directo   │ ──────────────────────> │ Elasticsearch DB │
│  (Source)   │                        │ (Indexed Data)   │
└─────────────┘                        └──────────────────┘
                                              │
                                              │ Query
                                              ▼
     ┌──────────────────────────────────────────────────┐
     │         ChatGPT-4 AI Assistant                   │
     │   (Natural Language → Analysis & Forecasting)    │
     └──────────────────────────────────────────────────┘
                          │
                          ▼
                    You get answers!
```

---

## First-Time Setup

### Prerequisites Checklist

Before using the system, ensure you have:

- [x] Python 3.8+ installed
- [x] pip package manager
- [x] Docker Desktop (for Elasticsearch)
- [x] Directo API token
- [x] OpenAI API key (ChatGPT)

### Step 1: Verify Elasticsearch is Running

```powershell
# Check if container is running
docker ps

# Should show: elasticsearch container with port 9200

# Test connection
curl http://localhost:9200

# Should return JSON with cluster info
```

**If not running:**
```powershell
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

### Step 2: Configure Your Credentials

**Edit the `.env` file:**

```env
# Directo API
DIRECTO_TOKEN=your_actual_token_here

# OpenAI API  
OPENAI_API_KEY=sk-your_actual_key_here

# Elasticsearch (usually no changes needed)
ES_HOST=localhost
ES_PORT=9200
```

**Where to get credentials:**
- **Directo Token**: Directo Settings → API Settings → Generate Token
- **OpenAI Key**: https://platform.openai.com/api-keys

### Step 3: Install Dependencies (First Time Only)

```powershell
pip install requests pandas openai elasticsearch schedule flask flask-cors
```

### Step 4: Verify Setup

```powershell
# Run the diagnostic tool
python fix_elasticsearch.py

# Run simple connection test
python simple_es_test.py
```

**Expected output:**
- ✓ Elasticsearch connected
- ✓ All tests passed

---

## Daily Usage

### Starting the System

You have **2 interface options**:

#### Option A: Console Interface (Recommended for Testing)

```powershell
python main_openai.py
```

**Menu Options:**
1. **Run ETL Pipeline** - Fetch fresh data from Directo
2. **Start Interactive Chat** - Ask questions about your data
3. **Answer Single Question** - One-off query
4. **Schedule Daily ETL** - Automate data updates
5. **Exit**

#### Option B: Web Interface (Recommended for Daily Use)

```powershell
python web_app_openai.py
```

Then open browser: **http://localhost:5000**

---

## Complete Workflow

### Your First Session (CRITICAL STEPS)

#### Step 1: Run ETL Pipeline (MUST DO FIRST!)

```powershell
python main_openai.py
# Select option: 1
```

**What happens:**
1. System connects to Directo API
2. Fetches all financial data (invoices, customers, purchases, etc.)
3. Indexes data into Elasticsearch
4. Makes data searchable

**Time required:** 5-15 minutes (depending on data volume)

**Expected output:**
```
INFO:directo_connector:Fetching all financial data from Directo...
INFO:directo_connector:Retrieved 1,250 invoices
INFO:directo_connector:Retrieved 340 customers
INFO:directo_connector:Retrieved 890 purchases
INFO:directo_connector:Retrieved 567 items
...
INFO:elasticsearch_indexer:Indexed 1250 documents to 'invoices'
INFO:__main__:ETL pipeline completed successfully!
```

**⚠️ IMPORTANT:** If you skip this step, the AI will have NO DATA to analyze!

#### Step 2: Verify Data Was Loaded

After ETL completes, verify data exists:

```powershell
# Quick check
curl http://localhost:9200/invoices/_count
curl http://localhost:9200/customers/_count
```

**Expected output:**
```json
{"count": 1250, ...}  // Should show number > 0
```

**If count is 0:**
- ETL didn't work
- Check Directo token is correct
- Check date range

#### Step 3: Start Asking Questions

```powershell
python main_openai.py
# Select option: 2 (Interactive Chat)
```

Or use web interface:
```powershell
python web_app_openai.py
# Open browser: http://localhost:5000
```

---

## Example Questions

### Simple Queries (Good for Testing)

```
"What were our total sales last month?"
"How many invoices did we issue in Q3?"
"List our top 5 customers by revenue"
"What's our average order value?"
```

### Multi-Dimensional Analysis (The Power!)

```
"How much of product X was sold in the Netherlands by each salesperson?"

"What was the sales profitability of service Y in Germany across all projects?"

"Show me revenue by country and region for salesperson John in the last quarter"

"Which item class performed best in each region?"

"Compare Q3 performance across all dimensions: country, product, salesperson"
```

### Forecasting

```
"Forecast our revenue for the next 6 months"

"Based on historical trends, what should we expect for Q1 2025 sales?"

"Predict costs for the next quarter"

"What's the projected growth rate for the Netherlands market?"
```

### Complex Business Questions

```
"Which salesperson has the best profit margin across all regions?"

"What are our top 5 most profitable products in the Netherlands?"

"How does our current quarter compare to the same quarter last year?"

"What percentage of our revenue comes from the top 10 customers?"

"Which projects are underperforming based on budget vs. actual?"
```

---

## Understanding ETL Pipeline

### What Gets Extracted from Directo?

The system fetches these data types:

| Data Type | What It Contains | Used For |
|-----------|------------------|----------|
| **Invoices** | Sales transactions, amounts, dates | Revenue analysis, forecasting |
| **Customers** | Customer details, countries, regions | Customer segmentation |
| **Purchases** | Cost data, suppliers | Cost analysis, profitability |
| **Items** | Products/services, classes, prices | Product analysis |
| **Projects** | Project details, managers | Project performance |
| **Objects** | Organizational structure | Multi-level analysis |
| **Accounts** | Chart of accounts | Financial categorization |
| **Suppliers** | Supplier information | Procurement analysis |

### Data Freshness

**How often should you run ETL?**

- **Daily** (recommended): Run at 2 AM automatically
- **Weekly**: For less dynamic businesses
- **On-demand**: Before important analysis

**To schedule daily ETL:**
```powershell
python main_openai.py
# Select option: 4
# Enter time: 02:00
```

### Date Ranges

By default, ETL fetches **last 2 years** of data.

**To change:**
```powershell
python main_openai.py
# Select option: 1
# When prompted, enter: 01.01.2024
```

---

## Typical Daily Workflow

### Morning Routine (Automated)

```
2:00 AM - Scheduled ETL runs automatically
         └─> Fetches new data from Directo
         └─> Updates Elasticsearch indices
         └─> System ready with fresh data
```

### During the Day (As Needed)

```powershell
# Option 1: Quick console query
python main_openai.py
# Select option 3
# Ask your question
# Get answer

# Option 2: Web interface (better for multiple queries)
python web_app_openai.py
# Use browser chat interface
```

---

## Troubleshooting

### Problem: "No data available" / AI says it can't find data

**Cause:** ETL hasn't been run or failed

**Solution:**
```powershell
# 1. Check if data exists
curl http://localhost:9200/invoices/_count

# 2. If count is 0, run ETL
python main_openai.py
# Select option 1

# 3. Check Directo token in .env
# Make sure DIRECTO_TOKEN is correct
```

### Problem: "Cannot connect to Elasticsearch"

**Cause:** Elasticsearch not running

**Solution:**
```powershell
# Check if running
docker ps

# If not listed, start it
docker start elasticsearch

# If doesn't exist, create it
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

### Problem: "OpenAI API error" / "Invalid API key"

**Cause:** OpenAI key incorrect or rate limited

**Solution:**
```powershell
# 1. Verify key in .env file
# OPENAI_API_KEY should start with sk-

# 2. Check at OpenAI dashboard
# https://platform.openai.com/api-keys

# 3. Check usage limits
# https://platform.openai.com/usage
```

### Problem: ETL runs but no data appears

**Cause:** Date range or Directo permissions

**Solution:**
```powershell
# 1. Check ETL logs for errors
python main_openai.py
# Look for "Retrieved X invoices" messages

# 2. Try shorter date range
# When prompted, enter: 01.11.2024

# 3. Verify Directo token has permissions
# Check in Directo: Settings → API
```

### Problem: Slow responses from AI

**Cause:** Large dataset or complex query

**Solutions:**
- **Use GPT-3.5-turbo for faster (cheaper) responses:**
  Edit `ai_query_handler_openai.py`, change `model="gpt-4o"` to `model="gpt-3.5-turbo"`
  
- **Narrow your queries:**
  Instead of: "Analyze everything"
  Try: "Analyze sales in Netherlands for last month"

### Problem: Connection timeout

**Cause:** Query too complex or network issue

**Solution:**
- Simplify the question
- Check internet connection
- Restart Elasticsearch

---

## Cost Management

### OpenAI API Costs

| Query Type | Estimated Cost | When to Use |
|------------|----------------|-------------|
| Simple query | $0.01-0.02 | Daily analysis |
| Complex multi-dimensional | $0.03-0.06 | Deep business insights |
| Forecasting (6 months) | $0.10-0.15 | Strategic planning |

**Tips to reduce costs:**
1. Use GPT-3.5-turbo for testing ($0.002 per query)
2. Be specific in questions (shorter = cheaper)
3. Batch related questions together
4. Use ETL scheduled (not manual repeated runs)

### Estimated Monthly Costs

**Light use** (10 queries/day): ~$5-10/month
**Medium use** (30 queries/day): ~$15-25/month  
**Heavy use** (100 queries/day): ~$50-80/month

---

## Best Practices

### Writing Good Questions

**✅ Good:**
- "What were sales in Netherlands for product X last quarter by salesperson?"
- "Forecast revenue for next 6 months based on 2024 trends"
- "Which projects had costs exceeding budget in Q3?"

**❌ Bad:**
- "Tell me everything" (too vague)
- "Analyze" (no specific question)
- "What happened?" (unclear context)

### Getting Better Answers

1. **Be specific about time periods**
   - "last quarter" vs. "last 3 months" vs. "Q3 2024"

2. **Mention dimensions explicitly**
   - "by country", "by salesperson", "by product class"

3. **Ask follow-up questions**
   - First: "What were top products last month?"
   - Then: "Show profitability breakdown for product X"

4. **Request specific formats**
   - "Show as a table"
   - "Give me top 10"
   - "Include percentages"

---

## For Your Thesis

### Demo Preparation

1. **Prepare 5-7 example queries** showing different capabilities:
   - Simple query
   - Multi-dimensional analysis  
   - Forecasting
   - Complex business question

2. **Show the contrast:**
   - "This query is impossible in Directo..."
   - "...but takes 10 seconds in our system"

3. **Measure metrics:**
   - Response time (aim for <5 seconds)
   - Query complexity (number of dimensions)
   - Forecast accuracy (compare predictions vs. actual)

### Key Talking Points

- **Problem:** Directo can't do multi-dimensional reporting without Excel
- **Solution:** AI + Elasticsearch enables natural language queries
- **Value:** Hours of manual work → 10-second query
- **Innovation:** First in Estonia for accounting systems?

---

## System Maintenance

### Weekly Tasks

```powershell
# Check system health
python fix_elasticsearch.py

# Verify data freshness
curl http://localhost:9200/invoices/_search?size=1&sort=transactiondate:desc
```

### Monthly Tasks

```powershell
# Update dependencies
pip install --upgrade openai elasticsearch

# Check Elasticsearch disk usage
docker exec elasticsearch df -h

# Review OpenAI API usage
# Visit: https://platform.openai.com/usage
```

---

## Getting Help

### Quick Diagnostics

```powershell
# Run full system check
python fix_elasticsearch.py

# Test Elasticsearch
python simple_es_test.py

# Check logs
python main_openai.py
# Watch for ERROR messages
```

### Common Error Messages

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "token required" | Directo token missing | Check .env file |
| "Cannot connect to Elasticsearch" | ES not running | Start Docker container |
| "Invalid API key" | OpenAI key wrong | Verify at platform.openai.com |
| "No data available" | ETL not run | Run option 1 first |
| "Rate limit exceeded" | Too many requests | Wait or upgrade OpenAI plan |

---

## FAQ

**Q: How much data can the system handle?**
A: Tested with 100,000+ invoices. Elasticsearch scales to millions.

**Q: Can multiple people use it simultaneously?**
A: Web interface supports multiple users, but each query costs API credits.

**Q: What if Directo adds new fields?**
A: Rerun ETL to pick up new data. May need to update index mappings.

**Q: Can I export results?**
A: Currently results are in chat. Future: Export to Excel/PDF.

**Q: Is my data secure?**
A: Local Elasticsearch = secure. OpenAI sees queries but not raw data.

**Q: What happens if I run out of OpenAI credits?**
A: Queries will fail. Add credits at platform.openai.com/billing

---

## Quick Reference Card

### Essential Commands

```powershell
# Start Elasticsearch
docker start elasticsearch

# Run ETL (get fresh data)
python main_openai.py  # Option 1

# Interactive chat
python main_openai.py  # Option 2

# Web interface
python web_app_openai.py

# Check system health
python fix_elasticsearch.py

# Test connection
python simple_es_test.py
```

### File Locations

- **Configuration**: `.env`
- **Main application**: `main_openai.py`
- **Web interface**: `web_app_openai.py`
- **Diagnostics**: `fix_elasticsearch.py`
- **ETL logic**: `directo_connector.py`
- **AI logic**: `ai_query_handler_openai.py`

---

## Support

For issues:
1. Run `python fix_elasticsearch.py`
2. Check logs in console
3. Verify .env configuration
4. Review this guide

---

**Remember:** Always run ETL (Option 1) before asking questions!

**Good luck with your thesis!** 🎓📊