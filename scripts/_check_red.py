import win32com.client

excel = win32com.client.Dispatch('Excel.Application')
excel.Visible = False
wb = excel.Workbooks.Open(r'C:\Users\KaiZs\Desktop\chaos\study\复习资料\practice\编程题抽出来的题库.xlsx')
ws = wb.Worksheets(1)

for row in range(2, 6):
    num = ws.Cells(row, 1).Value
    title = ws.Cells(row, 3).Value
    answer = ws.Cells(row, 5)
    text = answer.Text if answer.Text else ''
    print(f'Row {row}, Q{num}: {title}')
    print(f'  Answer len={len(text)}')

    # Show chars with non-default color
    chars = answer.Characters
    for i in range(1, min(200, len(text)) + 1):
        try:
            ch = chars(i, 1)
            c = ch.Text
            color = ch.Font.Color
            if color and color != 0 and color != 1:
                print(f'  [{i}] "{c}". Font.Color={color}')
        except:
            pass
    print()

wb.Close(False)
excel.Quit()
print('Done')
