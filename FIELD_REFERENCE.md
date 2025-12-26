# Directo API Field Reference Guide

Quick reference for correct field names when querying Elasticsearch indices.

## 📊 Invoices Index

### Key Financial Fields
- `netamount` (float) - Amount before VAT
- `vat` (float) - VAT amount
- `totalamount` (float) - Total invoice amount
- `balance` (float) - Outstanding balance

### Identification
- `number` (keyword) - Invoice number
- `customercode` (keyword) - Customer code
- `customername` (text) - Customer name

### Dates
- `date` (date) - Invoice date
- `transactiondate` (date) - Transaction date
- `duedate` (date) - Due date
- `ts` (date) - Last modified timestamp

### Location & Assignment
- `country` (keyword) - Country code (e.g., "GB", "EE")
- `salesman` (keyword) - Salesperson code

### Other Details
- `currency` (keyword) - Currency code (e.g., "EUR")
- `currencyrate` (float) - Exchange rate
- `vatzone` (keyword) - VAT zone
- `paymentterm` (keyword) - Payment terms
- `confirmed` (keyword) - Confirmation status
- `comment` (text) - Invoice comment
- `address1`, `address2`, `address3` (text) - Customer addresses

---

## 🛒 Purchases Index

### Key Financial Fields
- `sum` (float) - Total purchase amount (NOT "total")
- `vat` (float) - VAT amount

### Identification
- `number` (keyword) - Purchase number
- `supplier` (keyword) - Supplier code
- `suppliername` (text) - Supplier name
- `supplierinvoiceno` (keyword) - Supplier's invoice number

### Dates
- `date` (date) - Purchase date
- `duedate` (date) - Due date
- `transactiontime` (date) - Transaction timestamp
- `ts` (date) - Last modified timestamp

### Other Details
- `paymentterm` (keyword) - Payment terms
- `asset` (keyword) - Asset code
- `confirmed` (keyword) - Confirmation status

---

## 📦 Items Index

### Identification
- `code` (keyword) - Item code
- `name` (text) - Item name

### Classification
- `class` (keyword) - Item class code
- `class_name` (text) - Item class name
- `unit` (keyword) - Unit of measurement (e.g., "h" for hours)

### Pricing
- `salesprice` (float) - Base sales price
- `vatprice` (float) - Price with VAT
- `vatprice1`, `vatprice2`, `vatprice3`, `vatprice4` (float) - VAT price tiers
- `cost` (float) - Cost price

### Status
- `closed` (keyword) - Closed status

### Dates
- `ts` (date) - Last modified timestamp
- `tscreated` (date) - Creation timestamp

---

## 🎯 Projects Index

### Identification
- `code` (keyword) - Project code
- `name` (text) - Project name

### Organization
- `manager` (keyword) - Manager code
- `master` (keyword) - Master project code
- `type` (keyword) - Project type

### Dates
- `start` (date) - Start date
- `end` (date) - End date
- `createdts` (date) - Creation timestamp
- `ts` (date) - Last modified timestamp

### Other Details
- `country` (keyword) - Country code
- `closed` (keyword) - Closed status
- `points` (integer) - Points

---

## 👥 Customers Index

### Identification
- `code` (keyword) - Customer code
- `name` (text) - Customer name
- `regno` (keyword) - Registration number

### Classification
- `class` (keyword) - Customer class
- `type` (keyword) - Customer type

### Contact
- `email` (keyword) - Email address
- `address1`, `address2` (text) - Address lines

### Assignment
- `salesman` (keyword) - Assigned salesman
- `country` (keyword) - Country code

### Dates
- `ts` (date) - Last modified timestamp
- `ts_created` (date) - Creation timestamp

---

## 🏢 Objects Index

### Identification
- `code` (keyword) - Object code
- `name` (text) - Object name

### Classification
- `type` (keyword) - Object type (e.g., "Tehinguliik (TL)")
- `level` (keyword) - Level (stored as string, NOT integer)

### Dates
- `ts` (date) - Last modified timestamp

---

## 🔍 Common Query Examples

### Example 1: Revenue by Country
```json
{
  "indices": ["invoices"],
  "query": {"match_all": {}},
  "aggs": {
    "by_country": {
      "terms": {"field": "country"},
      "aggs": {
        "total_revenue": {"sum": {"field": "totalamount"}}
      }
    }
  }
}
```

### Example 2: Sales in Q4 2024
```json
{
  "indices": ["invoices"],
  "query": {
    "range": {
      "transactiondate": {
        "gte": "2024-10-01",
        "lte": "2024-12-31"
      }
    }
  },
  "aggs": {
    "total": {"sum": {"field": "netamount"}},
    "total_vat": {"sum": {"field": "vat"}}
  }
}
```

### Example 3: Top Customers by Revenue
```json
{
  "indices": ["invoices"],
  "query": {"match_all": {}},
  "aggs": {
    "top_customers": {
      "terms": {
        "field": "customercode",
        "size": 10,
        "order": {"revenue": "desc"}
      },
      "aggs": {
        "revenue": {"sum": {"field": "totalamount"}}
      }
    }
  }
}
```

### Example 4: Purchases by Supplier
```json
{
  "indices": ["purchases"],
  "query": {"match_all": {}},
  "aggs": {
    "by_supplier": {
      "terms": {"field": "supplier"},
      "aggs": {
        "total_spent": {"sum": {"field": "sum"}}
      }
    }
  }
}
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ WRONG → ✅ CORRECT

**Invoices:**
- ❌ `amount` → ✅ `netamount`
- ❌ `total` → ✅ `totalamount`
- ❌ `salesperson` → ✅ `salesman`
- ❌ `region` → ✅ Does not exist

**Purchases:**
- ❌ `total` → ✅ `sum`
- ❌ `amount` → ✅ Does not exist
- ❌ `date1` → ✅ `date`
- ❌ `date2` → ✅ `duedate`

**Items:**
- ❌ `price` → ✅ `salesprice` or `vatprice`
- ❌ `description` → ✅ Does not exist (use `name`)

**Projects:**
- ❌ `project_manager` → ✅ `manager`
- ❌ `customer` → ✅ Does not exist
- ❌ `region` → ✅ Does not exist

**Customers:**
- ❌ `phone` → ✅ Does not exist
- ❌ `region` → ✅ Does not exist

**Objects:**
- ❌ `level` as integer → ✅ `level` as keyword/string
- ❌ `master` → ✅ Does not exist
- ❌ `country` → ✅ Does not exist

---

**Last Updated**: December 26, 2025  
**Source**: Directo API XML structure via Postman
