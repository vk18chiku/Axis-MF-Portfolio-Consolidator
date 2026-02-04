# Portfolio data consolidation script
# Takes Excel file and converts to CSV format

import pandas as pd
import re
from datetime import datetime
import os


class PortfolioConsolidator:
    # Main class for processing portfolio data
    
    def __init__(self, excel_file_path, amc_name="Axis Mutual Fund"):
        self.excel_file_path = excel_file_path
        self.amc_name = amc_name
        self.excel_file = pd.ExcelFile(excel_file_path)
        self.reporting_date = None
        
    def extract_reporting_date(self, df):
        # try to find the date from sheet
        for i in range(min(10, len(df))):
            for col in df.columns:
                cell_value = str(df.iloc[i, col])
                if 'December 31' in cell_value or 'december 31' in cell_value.lower():
                    match = re.search(r'202[0-9]', cell_value)
                    if match:
                        return "2025-12-31"
        return "2025-12-31"  # default dec 2025
    
    def parse_scheme_sheet(self, sheet_name, scheme_full_name):
        # Parse individual scheme sheet for equity and debt data
        df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name, header=None)
        
        if not self.reporting_date:
            self.reporting_date = self.extract_reporting_date(df)
        
        equity_holdings = []
        debt_holdings = []
        
        # find the header row
        header_row_idx = None
        for i in range(min(20, len(df))):
            row_text = ' '.join([str(x) for x in df.iloc[i].values])
            if 'Name of the Instrument' in row_text and 'ISIN' in row_text:
                header_row_idx = i
                break
        
        if header_row_idx is None:
            return pd.DataFrame(), pd.DataFrame()
        
        current_type = None
        is_data_row = False
        
        for idx in range(header_row_idx + 1, len(df)):
            row = df.iloc[idx]
            row_str = ' '.join([str(x) for x in row.values if pd.notna(x)])
            
            # check section type
            if 'Equity' in row_str and 'related' in row_str:
                current_type = 'Equity'
                is_data_row = True
                continue
            elif 'Debt Instruments' in row_str:
                current_type = 'Debt'
                is_data_row = True
                continue
            elif 'Sub Total' in row_str or 'GRAND TOTAL' in row_str or 'Grand Total' in row_str:
                continue
            elif 'Listed' in row_str or 'Unlisted' in row_str or 'Privately placed' in row_str:
                continue
            elif 'Reverse Repo' in row_str or 'TREPS' in row_str or 'Net Receivables' in row_str:
                continue
                
            if current_type and is_data_row:
                # extract instrument details
                instrument_code = str(row.iloc[0]) if pd.notna(row.iloc[0]) else None
                instrument_name = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else None
                isin = str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else None
                if not instrument_name or instrument_name == 'nan' or instrument_name == 'NaN':
                    continue
                if instrument_name in ['Sub Total', 'Total', 'GRAND TOTAL']:
                    continue
                    
                percentage = None
                for col_idx in [6, 5, 7]:  # try different columns
                    if len(row) > col_idx:
                        val = row.iloc[col_idx]
                        if pd.notna(val):
                            try:
                                percentage = float(val)
                                break
                            except:
                                pass
                
                if instrument_name and percentage is not None:
                    holding = {
                        'amc_name': self.amc_name,
                        'scheme_name': scheme_full_name,
                        'scheme_code': sheet_name,
                        'instrument_code': instrument_code if instrument_code != 'nan' else None,
                        'instrument_name': instrument_name,
                        'instrument_type': current_type,
                        'isin': isin if isin and isin != 'nan' and len(isin) == 12 else None,
                        'portfolio_percentage': percentage,
                        'reporting_date': self.reporting_date
                    }
                    
                    if current_type == 'Equity':
                        equity_holdings.append(holding)
                    elif current_type == 'Debt':
                        debt_holdings.append(holding)
        
        return pd.DataFrame(equity_holdings), pd.DataFrame(debt_holdings)
    
    def get_scheme_list(self):
        # get all schemes from index sheet
        index_df = pd.read_excel(self.excel_file_path, sheet_name="Index", header=0)
        
        schemes = {}
        for _, row in index_df.iterrows():
            if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                short_name = str(row.iloc[1]).strip()
                full_name = str(row.iloc[2]).strip()
                if short_name and full_name and short_name != 'Short Name':
                    schemes[short_name] = full_name
        
        return schemes
    
    def consolidate_all_schemes(self):
        # process all schemes and consolidate data
        schemes = self.get_scheme_list()
        print(f"Found {len(schemes)} schemes to process")
        
        all_equity = []
        all_debt = []
        
        cnt = 0
        for scheme_code, scheme_name in schemes.items():
            try:
                equity_df, debt_df = self.parse_scheme_sheet(scheme_code, scheme_name)
                
                if not equity_df.empty:
                    all_equity.append(equity_df)
                if not debt_df.empty:
                    all_debt.append(debt_df)
                
                cnt += 1
                if cnt % 10 == 0:
                    print(f"Processed {cnt}/{len(schemes)} schemes...")
                    
            except Exception as e:
                print(f"Error processing {scheme_code}: {str(e)}")
                continue
        
        print(f"\nSuccessfully processed {cnt} schemes")
        
        # combine everything
        equity_consolidated = pd.concat(all_equity, ignore_index=True) if all_equity else pd.DataFrame()
        debt_consolidated = pd.concat(all_debt, ignore_index=True) if all_debt else pd.DataFrame()
        
        return equity_consolidated, debt_consolidated
    
    def save_to_csv(self, equity_df, debt_df, output_dir="output"):
        # save data to csv files
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        
        if not equity_df.empty:
            equity_file = os.path.join(output_dir, f"equity_holdings_{timestamp}.csv")
            equity_df.to_csv(equity_file, index=False)
            print(f"\n✓ Equity holdings saved: {equity_file}")
            print(f"  Total equity holdings: {len(equity_df)}")
        
        if not debt_df.empty:
            debt_file = os.path.join(output_dir, f"debt_holdings_{timestamp}.csv")
            debt_df.to_csv(debt_file, index=False)
            print(f"✓ Debt holdings saved: {debt_file}")
            print(f"  Total debt holdings: {len(debt_df)}")
        
        if not equity_df.empty or not debt_df.empty:
            combined_df = pd.concat([equity_df, debt_df], ignore_index=True)
            combined_file = os.path.join(output_dir, f"all_holdings_{timestamp}.csv")
            combined_df.to_csv(combined_file, index=False)
            print(f"✓ Combined holdings saved: {combined_file}")
            print(f"  Total holdings: {len(combined_df)}")
        
        self.generate_summary(equity_df, debt_df, output_dir)
    
    def generate_summary(self, equity_df, debt_df, output_dir):
        summary = []
        
        summary.append("=" * 80)
        summary.append("PORTFOLIO CONSOLIDATION SUMMARY")
        summary.append("=" * 80)
        summary.append(f"AMC Name: {self.amc_name}")
        summary.append(f"Reporting Date: {self.reporting_date}")
        summary.append(f"Total Schemes: {len(self.get_scheme_list())}")
        summary.append("")
        
        if not equity_df.empty:
            summary.append("EQUITY HOLDINGS:")
            summary.append(f"  Total Holdings: {len(equity_df)}")
            summary.append(f"  Unique Instruments: {equity_df['instrument_name'].nunique()}")
            summary.append(f"  Schemes with Equity: {equity_df['scheme_name'].nunique()}")
        
        if not debt_df.empty:
            summary.append("\nDEBT HOLDINGS:")
            summary.append(f"  Total Holdings: {len(debt_df)}")
            summary.append(f"  Unique Instruments: {debt_df['instrument_name'].nunique()}")
            summary.append(f"  Schemes with Debt: {debt_df['scheme_name'].nunique()}")
        
        summary.append("=" * 80)
        
        summary_text = "\n".join(summary)
        print("\n" + summary_text)
        
        summary_file = os.path.join(output_dir, "summary.txt")
        with open(summary_file, 'w') as f:
            f.write(summary_text)


def main():
    print("=" * 80)
    print("QONFIDO ASSIGNMENT - PORTFOLIO DATA CONSOLIDATION")
    print("=" * 80)
    print()
    
    excel_file = "Monthly Portfolio-31 12 25.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"Error: File '{excel_file}' not found!")
        return
    
    consolidator = PortfolioConsolidator(excel_file, amc_name="Axis Mutual Fund")
    
    print("Starting consolidation process...\n")
    equity_df, debt_df = consolidator.consolidate_all_schemes()
    
    print("\nSaving results to CSV files...")
    consolidator.save_to_csv(equity_df, debt_df)
    
    print("\n" + "=" * 80)
    print("CONSOLIDATION COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
