# Insurance Actuarial Analysis Sample

## 📊 **Data Structure**

### CSV Fields:
- **LoB_masked**: Line of Business (1=Property, 2=Casualty, 3=Marine, 4=Aviation, 5=Reinsurance)
- **AccidentYear**: Policy effective year (2019-2021)
- **DevelopmentYear**: Years since accident (1-2)
- **ActualIncurred**: Total incurred losses ($)
- **NominalReserves**: Nominal reserve value ($)
- **DiscountedReserves**: Present value reserves ($)
- **OCL**: Outstanding Claims Liability ($)
- **ChangeInOcl**: Change in OCL from previous period ($)
- **BusinessSegment**: Descriptive segment name

## 🎯 **Generated Slides**

### Slide 1: Reserves Summary
| (empty) | Actual Incurred | Nominal Reserves | Discounted Reserves |
|---------|----------------|-----------------|-------------------|
| **Total** | **$42,500,000** | **$34,000,000** | **$33,450,000** |
| Outstanding Claims Liability | - | - | $3,285,000 |
| Change in OCL | - | - | $615,000 |

### Slide 2: Line of Business Breakdown  
| (empty) | OCL |
|---------|-----|
| Property (LOB1) | $615,000 |
| Casualty (LOB2) | $1,050,000 |
| Marine (LOB3) | $470,000 |
| Aviation (LOB4) | $383,000 |
| Reinsurance (LOB5) | $1,050,000 |

### Slide 3: Reserve Development
| (empty) | Amount |
|---------|--------|
| Total Incurred | $42,500,000 |
| Nominal Reserves | $34,000,000 |
| Discounted Reserves | $33,450,000 |

## 🔧 **Key Features Implemented**

✅ **Insurance-specific field names** (ActualIncurred, OCL, etc.)  
✅ **Line of Business filtering** (LoB_masked with filters)  
✅ **Group headers with spans_all_columns**  
✅ **Currency formatting** for all financial fields  
✅ **Real data calculations** with sum aggregations  
✅ **Filter support** for LoB breakdowns  
✅ **Component_rows support** for aggregated totals  

## 🎨 **Styling**

- **Group Headers**: Bold, light gray background, spans all columns
- **Financial Values**: Currency format ($1,234,567)  
- **Empty Cells**: Show "-" when no data
- **Table Layout**: First column for labels, metric fields as columns

This matches the insurance/actuarial domain requirements with proper reserve analysis, line of business breakdowns, and financial formatting.
