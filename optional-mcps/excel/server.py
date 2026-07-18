from mcp.server.fastmcp import FastMCP
import pandas as pd
import json
import os

mcp = FastMCP("mcp-excel")

@mcp.tool()
def excel_list_sheets(file_path: str) -> str:
    """List all sheet names inside an Excel workbook (.xlsx or .xlsm).
    
    Args:
        file_path: The absolute or relative path to the Excel file.
    """
    try:
        xls = pd.ExcelFile(file_path)
        return json.dumps({"success": True, "sheets": xls.sheet_names})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def excel_read_sheet(file_path: str, sheet_name: str, nrows: int = 100) -> str:
    """Read the contents of a specific Excel sheet and return it as a JSON table.
    
    Args:
        file_path: The absolute or relative path to the Excel file.
        sheet_name: The name of the worksheet to read.
        nrows: Maximum number of rows to read (default 100).
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=nrows)
        # Convert NaN values to None for clean JSON serialization
        df = df.where(pd.notnull(df), None)
        data = df.to_dict(orient="records")
        return json.dumps({"success": True, "columns": df.columns.tolist(), "data": data}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def excel_search_cells(file_path: str, query: str) -> str:
    """Search for a specific string query in all cells across all sheets in the Excel file.
    
    Args:
        file_path: The absolute or relative path to the Excel file.
        query: The string to search for (case-insensitive).
    """
    try:
        xls = pd.ExcelFile(file_path)
        results = []
        query_lower = query.lower()
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            for row_idx, row in df.iterrows():
                for col_idx, val in enumerate(row):
                    if pd.notna(val) and query_lower in str(val).lower():
                        results.append({
                            "sheet": sheet_name,
                            "row": int(row_idx) + 1,  # 1-based index
                            "col": int(col_idx) + 1,  # 1-based index
                            "value": str(val)
                        })
        return json.dumps({"success": True, "matches": results}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

if __name__ == "__main__":
    mcp.run()
