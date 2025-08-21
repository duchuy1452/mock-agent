# PowerPoint Table Structure Example

## Input Data (CSV):
```csv
date,region,product,sales_amount,units_sold,customer_type
2024-01-15,North,Laptop,1250.00,5,Corporate
2024-01-16,South,Mouse,25.99,50,Individual
...
```

## Field Configuration (JSON):
```json
[
  {
    "row_label": "Total Revenue",
    "metric_fields": ["sales_amount"],
    "is_group_header": false,
    "aggregation": "sum"
  },
  {
    "row_label": "Sales by Region", 
    "metric_fields": ["sales_amount", "units_sold"],
    "is_group_header": true,
    "spans_all_columns": false,
    "aggregation": "sum"
  },
  {
    "row_label": "Unit Sales",
    "metric_fields": ["units_sold"],
    "is_group_header": false,
    "aggregation": "sum"
  }
]
```

## Generated PowerPoint Table:

| (empty) | Sales Amount | Units Sold |
|---------|-------------|------------|
| **Total Revenue** | $27,750 | - |
| **Sales by Region** | $27,750 | 439 |
| Unit Sales | - | 439 |

## Logic:
1. **Columns**: All unique metric_fields = ["sales_amount", "units_sold"]
2. **Rows**: Each row_label becomes a table row
3. **Values**: 
   - If row uses that metric_field → calculate aggregation
   - If row doesn't use that metric_field → empty cell "-"
4. **Styling**:
   - Group headers: Bold, light gray background
   - spans_all_columns: Group header text spans entire row
   - Regular data: Right-aligned numbers

## Key Improvements:
✅ No "Metric" column header  
✅ Row labels in first column  
✅ Metric fields as column headers  
✅ Real data calculations with aggregations  
✅ Smart formatting (currency, numbers)  
✅ Proper group header styling  
✅ Error handling for missing fields  
