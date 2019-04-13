# xls_tool.py
# Write matrix to a xls or Read matrix from xls
import xlrd
import xlwt
from typing import List


def write_xls(file_name: str, matrix: List[List]):
    book_out = xlwt.Workbook()
    sheet_out = book_out.add_sheet(file_name)
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix[i])):
            sheet_out.write(i, j, matrix[i][j])
    book_out.save(file_name)


def read_xls(file_name: str, sheet_idx=0, has_head=False, limit=(0, 0)) -> List[List]:
    book = xlrd.open_workbook(file_name)
    sheet = book.sheet_by_index(sheet_idx)
    result_mat = []
    for i in range(1 if has_head else 0, sheet.nrows if limit[0] == 0 else limit[0]):
        result_mat.append([0 if x == "" else x for x in sheet.row_values(i)])
    return result_mat

