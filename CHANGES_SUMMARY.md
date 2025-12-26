# Elasticsearch Index Mapping Corrections

## Summary
Fixed Elasticsearch index mappings to match the actual XML structure from Directo API. The previous mappings had incorrect field names which prevented OpenAI from successfully querying and analyzing the data.

## Changes Made

### 1. **Invoice Index** (`invoices`)

#### Previous (Incorrect) Fields:
- `amount` → ❌ Does not exist in Directo XML
- `total` → ❌ Does not exist in Directo XML
- `region` → ❌ Does not exist in Directo XML
- `salesperson` → ❌ Does not exist in Directo XML
- `project` → ❌ Does not exist in Directo XML

#### New (Correct) Fields:
- ✅ `netamount` - The net amount before VAT
- ✅ `vat` - VAT amount
- ✅ `totalamount` - Total invoice amount (replaces "total")
- ✅ `balance` - Outstanding balance
- ✅ `salesman` - Salesperson code (replaces "salesperson")
- ✅ `customername` - Customer name (text field)
- ✅ `vatzone` - VAT zone
- ✅ `paymentterm` - Payment terms
- ✅ `currency` - Currency code
- ✅ `currencyrate` - Exchange rate
- ✅ `comment` - Invoice comment
- ✅ `address1`, `address2`, `address3` - Customer address fields
- ✅ `confirmed` - Confirmation status

### 2. **Purchase Index** (`purchases`)

#### Previous (Incorrect) Fields:
- `date1` → ❌ Does not exist
- `date2` → ❌ Does not exist
- `amount` → ❌ Does not exist
- `total` → ❌ Does not exist
- `status` → ❌ Does not exist

#### New (Correct) Fields:
- ✅ `date` - Purchase date
- ✅ `duedate` - Due date
- ✅ `sum` - Total sum (replaces "total")
- ✅ `supplierinvoiceno` - Supplier's invoice number
- ✅ `paymentterm` - Payment terms
- ✅ `suppliername` - Supplier name (text field)
- ✅ `transactiontime` - Transaction timestamp
- ✅ `asset` - Asset code
- ✅ `confirmed` - Confirmation status

### 3. **Item Index** (`items`)

#### Previous (Incorrect) Fields:
- `type` → ❌ Does not exist
- `barcode` → ❌ Does not exist
- `supplier` → ❌ Does not exist
- `supplieritem` → ❌ Does not exist
- `description` → ❌ Does not exist
- `price` → ❌ Does not exist (ambiguous)

#### New (Correct) Fields:
- ✅ `class_name` - Item class name
- ✅ `unit` - Unit of measurement
- ✅ `salesprice` - Sales price
- ✅ `vatprice` - Price with VAT
- ✅ `vatprice1`, `vatprice2`, `vatprice3`, `vatprice4` - Different VAT price tiers
- ✅ `cost` - Cost price
- ✅ `closed` - Closed status
- ✅ `tscreated` - Creation timestamp

### 4. **Project Index** (`projects`)

#### Previous (Incorrect) Fields:
- `customer` → ❌ Does not exist
- `supplier` → ❌ Does not exist
- `orderer` → ❌ Does not exist
- `contract` → ❌ Does not exist
- `project_manager` → ❌ Does not exist
- `region` → ❌ Does not exist

#### New (Correct) Fields:
- ✅ `name` - Project name
- ✅ `manager` - Manager code (replaces "project_manager")
- ✅ `start` - Start date
- ✅ `end` - End date
- ✅ `master` - Master project code
- ✅ `type` - Project type
- ✅ `points` - Points (integer)
- ✅ `createdts` - Creation timestamp

### 5. **Customer Index** (`customers`)

#### Previous (Incorrect) Fields:
- `loyaltycard` → ❌ Does not exist
- `phone` → ❌ Does not exist
- `closed` → ❌ Does not exist
- `region` → ❌ Does not exist

#### New (Correct) Fields:
- ✅ `class` - Customer class
- ✅ `type` - Customer type
- ✅ `salesman` - Assigned salesman
- ✅ `address1`, `address2` - Address fields
- ✅ `ts_created` - Creation timestamp

### 6. **Object Index** (`objects`)

#### Previous (Incorrect) Fields:
- `master` → ❌ Does not exist
- `level` as integer → ❌ Wrong type (should be keyword/string)
- `country` → ❌ Does not exist
- `region` → ❌ Does not exist

#### New (Correct) Fields:
- ✅ `name` - Object name
- ✅ `type` - Object type (e.g., "Tehinguliik (TL)")
- ✅ `level` - Level as keyword/string (not integer)

## Impact on OpenAI Queries

The AI query handler (`ai_query_handler_openai.py`) has been updated with the correct field names. This means:

1. ✅ Revenue queries can now use `netamount`, `vat`, and `totalamount`
2. ✅ Purchase queries can use `sum` instead of non-existent `total`
3. ✅ Date filtering works correctly with `transactiondate` for invoices
4. ✅ Customer filtering uses `customercode` and `customername`
5. ✅ Salesperson filtering uses `salesman` (not `salesperson`)

## Example Query Improvements

### Before (Would Fail):
```json
{
  "indices": ["invoices"],
  "query": {
    "range": {
      "amount": {"gte": 1000}  // ❌ Field doesn't exist
    }
  }
}
```

### After (Will Succeed):
```json
{
  "indices": ["invoices"],
  "query": {
    "range": {
      "netamount": {"gte": 1000}  // ✅ Correct field
    }
  },
  "aggs": {
    "total_revenue": {
      "sum": {"field": "totalamount"}  // ✅ Correct field
    }
  }
}
```

## Testing Recommendations

After deploying these changes:

1. **Delete existing indices** to remove old mappings:
   ```python
   python test_serverless.py
   # Then manually delete indices through Kibana or API
   ```

2. **Re-run ETL pipeline** to index data with correct mappings:
   ```python
   python main_openai.py
   # Choose Option 1: Run ETL Pipeline
   ```

3. **Verify data** is correctly indexed:
   ```python
   python verify_data_quick.py
   ```

4. **Test queries** through the interactive chat:
   ```python
   python main_openai.py
   # Choose Option 2: Start Interactive Chat
   # Try: "What were our total sales in Great Britain last quarter?"
   ```

## Files Modified

1. ✅ `elasticsearch_indexer.py` - Fixed all index mappings
2. ✅ `ai_query_handler_openai.py` - Updated field names in prompts

## Migration Steps

1. Backup current data (if needed)
2. Delete existing Elasticsearch indices
3. Deploy updated code
4. Run ETL pipeline to re-index with correct mappings
5. Test queries to ensure AI can now successfully analyze data

---

**Date**: December 26, 2025  
**Issue**: Incorrect Elasticsearch index mappings causing AI query failures  
**Resolution**: Updated mappings to match actual Directo API XML structure
