from openpyxl import Workbook
from openpyxl.styles import Font, Alignment



def generate_excel_report(all_purchases, file_path):
    total_spent = 0
    total_buy_subscription = 0
    all_subscription = []

    for purshases in all_purchases:
        total_buy_subscription += 1
        total_spent += purshases['subscription_price']

    sub_name_price = [f"{i['subscription_name']} {i['subscription_price']}" for i in all_purchases]
    mapped_sub = set(sub_name_price)   

    for sub_name in mapped_sub:
        count_sub_name = 0
        for i in sub_name_price:
            if i == sub_name:
                count_sub_name += 1

        all_subscription.append(
                {
                    'sub_name':sub_name.split(' ')[0],
                    'sub_price':sub_name.split(' ')[1],
                    'sub_count':count_sub_name
                }
        )


    all_subscription =  sorted(all_subscription,key=lambda sub: int(sub['sub_name']), reverse=True)

    workbook = Workbook()
    sheet = workbook.active

    sheet.column_dimensions['A'].width=20
    sheet.column_dimensions['B'].width=15
    sheet.column_dimensions['C'].width=15
    sheet.column_dimensions['D'].width=20


    sheet['A1'] = 'Название абонемента'
    sheet['A1'].font=Font(bold=True)


    sheet['B1'] = 'Цена абонемента'
    sheet['B1'].alignment=Alignment(horizontal='center', wrap_text=True)
    sheet['B1'].font=Font(bold=True)

    sheet['C1'] = 'Кол-во проданных'
    sheet['C1'].alignment=Alignment(horizontal='center', wrap_text=True)
    sheet['C1'].font=Font(bold=True)

    sheet['D1'] = 'Потрачено всего'
    sheet['D1'].alignment=Alignment(horizontal='center', wrap_text=True)
    sheet['D1'].font=Font(bold=True)


    for line, sub in enumerate(all_subscription, start=2):
        sheet[f'A{line}'] = sub['sub_name']
        sheet[f'B{line}'] = sub['sub_price']
        sheet[f'B{line}'].alignment=Alignment(horizontal='center')
        sheet[f'C{line}'] = sub['sub_count']
        sheet[f'C{line}'].alignment=Alignment(horizontal='center')

        sheet[f'D{line}'] = int(sub['sub_price'])*int(sub['sub_count'])
        sheet[f'D{line}'].alignment=Alignment(horizontal='center')

    sheet[f'C{line+2}'] = "Всего потрачено:"
    sheet[f'D{line+2}'] = total_spent
    sheet[f'D{line+2}'].alignment=Alignment(horizontal='center')

    sheet[f'C{line+3}'] = "Всего продано:"
    sheet[f'D{line+3}'] = total_buy_subscription
    sheet[f'D{line+3}'].alignment=Alignment(horizontal='center')



    workbook.save(filename=file_path)
