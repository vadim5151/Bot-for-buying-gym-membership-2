def format_price_list(price_data):
    price_list = 'Актуальный прайс лист:\n'
    for price in sorted(price_data, key=lambda x: x['month']):
        if price['month'] == 1:
            price_list += f'{price['month']} месяц: {price['price']}₽\n'
        elif 1<price['month'] and price['month']<5:
            price_list += f'{price['month']} месяца: {price['price']}₽\n'
        elif price['month'] >= 5:
            price_list += f'{price['month']} месяцев: {price['price']}₽\n'
    
    return price_list


def format_subscription(all_purchases):

    header = '| Период |  Цена  | Кол-во шт |'
    line = f"{'-'*len(header)}\n"
    
    text = f"```\n{line + header + '\n|--------|--------|-----------|\n'}"
    sub_name_price = [f"{i['month']} {i['amount']}" for i in all_purchases]
    mapped_sub = set(sub_name_price)   

    all_subscription = []

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

    for purchase in sorted(all_subscription,key=lambda sub: int(sub['sub_name']), reverse=True):
        price = f"{int(purchase['sub_price']):_}"
        text += f"|{purchase['sub_name'].center(8)}|{price.center(8)}|{str(purchase['sub_count']).center(11)}|\n"

    text += f"{'-'*len(header)}\n```"

    total_spent = 0
    total_buy_subscription = 0

    for purshase in all_purchases:
        total_buy_subscription += 1
        total_spent += purshase['amount']

    text += f'''
Всего продано абонементов: *{total_buy_subscription}*
На сумму: *{total_spent:_}₽*
    '''
    
    return text


def format_price(month, amount):
    price = ''
    if int(month) == 1:
        price += f'{month} месяц: {amount}₽\n'
    elif 1<int(month) and int(month)<5:
        price += f'{month} месяца: {amount}₽\n'
    elif int(month) >= 5:
        price += f'{month} месяцев: {amount}₽\n'
    return price


def format_cheque(month, today_date, new_expiration_date, amount):
    cheque = ''

    if int(month) == 1:
        cheque += 'Поздравляем с покупкой абонемента на месяц!\n'
    elif 1<int(month)<5:
        cheque += f'Поздравляем с покупкой абонемента на {month} месяца!\n'
    else:
        cheque += f'Поздравляем с покупкой абонемента на {month} месяцев!\n'
    
    cheque += f'''Дата покупки: {today_date}
Дата окончания абонемента: {new_expiration_date}
Стоимость: {amount}
Желаем вам продуктивных тренировок и ярких эмоций!'''
    return cheque


def format_articles(article):
    url_article = article['url_article']

    return f'<b>{article['title']}</b>\n{article['text']}', url_article





