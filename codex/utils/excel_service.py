from pathlib import Path
from openpyxl import Workbook, load_workbook

HEADERS = [
    "Id",
    "Titre de l'article",
    "Auteur",
    "DOI",
    "Date de publication",
    "Lien de l'article",
    "Conjecture",
]

def create_excel_file(excel_file: str, sheet_name: str = "Sheet1"):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    ws.append(HEADERS)

    Path(excel_file).parent.mkdir(parents=True, exist_ok=True)
    wb.save(excel_file)

def open_excel_file(excel_file: str):
    return load_workbook(excel_file)
