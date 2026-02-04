# Mutual Fund Portfolio Data Consolidation

## Overview

This project consolidates mutual fund portfolio data from Excel files into structured CSV format. Built for Axis Mutual Fund but designed to work with any AMC.

---

## What It Does

- Downloads portfolio data from AMC websites
- Parses Excel files with multiple sheets
- Consolidates holdings into clean CSV format
- Validates data quality  

---

## Data Schema

The CSV files use this structure:

- `amc_name` - AMC identifier
- `scheme_name` - Full scheme name
- `scheme_code` - Short code
- `instrument_code` - Internal code (if available)
- `instrument_name` - Security/instrument name
- `instrument_type` - Equity or Debt
- `isin` - ISIN code (12 chars, may be null)
- `portfolio_percentage` - % of portfolio
- `reporting_date` - Date in YYYY-MM-DD format

### Files Generated

- `equity_holdings_YYYYMMDD.csv` - All equity investments
- `debt_holdings_YYYYMMDD.csv` - All debt instruments
- `all_holdings_YYYYMMDD.csv` - Combined data

---

## Files

- `consolidate_portfolio.py` - Main script for data processing
- `download_portfolio.py` - Web automation for downloads
- `validate_data.py` - Data quality checks
- `analyze_excel.py` - Excel file analysis
- `requirements.txt` - Python dependencies
- `output/` - Generated CSV files

---

## Setup

### Requirements

- Python 3.8+
- Chrome browser (optional, for automation)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Process Portfolio Data

```bash
python consolidate_portfolio.py
```

This will read the Excel file and generate CSV files in the `output/` folder.

### Download Data (Optional)

```bash
python download_portfolio.py
```

Choose from:
1. Selenium automation (needs Chrome)
2. Simple HTTP download
3. Manual instructions

### Validate Output

```bash
python validate_data.py
```

Shows data quality metrics and statistics.

---

## How It Works

### Web Scraping

Two methods:
1. **Selenium** - Full browser automation for JavaScript sites
2. **Requests** - Simple HTTP download for static pages

### Data Processing

1. Load Excel file
2. Find header rows in each sheet
3. Identify equity vs debt sections
4. Extract holdings with percentages
5. Consolidate into single dataset
6. Export to CSV

### Error Handling

- Skips problematic sheets
- Continues on parsing errors
- Handles missing ISINs
- Reports progress

---

## Results

- 87 schemes processed
- 5,313 total holdings extracted
- 3,709 equity holdings
- 1,604 debt holdings
- 92.9% ISIN coverage
- Processing time: ~10 seconds

---

## Libraries Used

- pandas - Data processing
- openpyxl - Excel files
- selenium - Browser automation
- beautifulsoup4 - HTML parsing
- requests - HTTP downloads

---

## Using with Other AMCs

To adapt for another AMC:

1. Change URL in `download_portfolio.py`
2. Update AMC name:
```python
consolidator = PortfolioConsolidator(
    excel_file="portfolio.xlsx",
    amc_name="Your AMC Name"
)
```
3. May need to adjust header detection based on format

---

## 🧪 Testing & Validation

### Manual Validation Steps

1. **Row Count Check**: Verify number of holdings matches manual count
2. **Sample Verification**: Cross-check 5-10 random entries with source
3. **Percentage Sum**: Ensure percentages per scheme ≈ 100%
4. **ISIN Validation**: Check ISIN format (12 alphanumeric)
5. **Data Types**: Verify all fields have correct types

### Known Limitations

1. **Format Variations**: Some schemes may have unique layouts
2. **Missing ISINs**: Some instruments don't have ISIN codes
3. **Sub-totals**: Manual filtering needed if included
4. **Dynamic Content**: Website structure changes may break automation

---

## 📝 Assumptions

1. **Excel Format**: All scheme sheets follow similar structure
2. **Date Format**: Reporting date is December 31, 2025
3. **Header Row**: Contains "Name of the Instrument" and "ISIN"
4. **Section Headers**: Equity/Debt sections clearly marked
5. **Percentage Column**: Located in column 6 (may vary)

---

## 🚨 Troubleshooting

### Issue: Selenium not working
**Solution**: Install Chrome and ChromeDriver
```bash
pip install webdriver-manager
```

### Issue: Excel parsing errors
**Solution**: Check if file format matches expected structure
```bash
python analyze_excel.py  # Run analysis first
```

### Issue: Missing data in CSV
**Solution**: Some schemes may have non-standard formats
- Check error messages during processing
- Manually verify problematic sheets

### Issue: Download automation fails
**Solution**: Use manual download option
```bash
python download_portfolio.py  # Select option 3
```

---

## 🎓 Learning Outcomes

1. **Real-world Data Wrangling**: Handling messy, unstructured data
2. **Web Automation**: Selenium for dynamic content
3. **Data Modeling**: Generic schema design
4. **ETL Pipeline**: Extract, Transform, Load workflow
5. **Python Best Practices**: OOP, type hints, documentation

---

## 📧 Contact

For questions or clarifications about this implementation:
- **Email**: [uttam.2023ug4003@iiitranchi.ac.in]

---



