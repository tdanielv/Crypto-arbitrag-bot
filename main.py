import collections
import json
import time

from poloniex import Poloniex

COMMISSION = 0.0025

CONFIG_FILE = 'resources/pairs.json'
MAIN_ACTIVE = ['BTC', 'ETH']


def split(str):
    return str.split('_')


def coin_pairs():
    '''Первоначально я загружаю список пар валют
    (находится в pairs.json, тут вы можете задать свои пары),
    за которыми будет следить бот с помощью функции coin_pairs.'''
    with open(CONFIG_FILE) as file_data:
        data = json.load(file_data)

    return data
#
#
def create_dictionary(pairs):
    '''сформируем стоимость активов относительно других активов.'''
    # стакан
    order_book = polo.returnOrderBook(depth=1)
    dictionary = collections.defaultdict(dict)
    # print(order_book)

    for pair in pairs:
        p = pair.upper()
        src, dst = split(p)

        # ордера на прождажу
        ask_order = order_book[p]['asks'][0]
        src_ask = {
            'pair': src + '_' + dst,
            'price': float(ask_order[0]),
            'amount': float(ask_order[1])
        }
        # print(src_ask)

        bid_order = order_book[p]['bids'][0]
        src_bid = {
            'pair': dst + '_' + src,
            'price': 1 / float(bid_order[0]),
            'amount': float(bid_order[1]) * float(bid_order[0])
        }

        dictionary[src][dst] = src_ask
        dictionary[dst][src] = src_bid
        # print(dictionary)
    return dictionary


def get_amount():
    try:
        amount_3 = order_3['amount'] * order_3['price']
        print('amount_3----', amount_3)

        amount_2 = order_2['amount'] if order_2['amount'] < amount_3 else amount_3

        amount_2 = amount_2 * order_2['price']
        print('amount_1----', order_1['amount'])
        return order_1['amount'] if order_1['amount'] < amount_2 else amount_2
    except TypeError:
        return 0

while True:
    polo = Poloniex()
    pairs = coin_pairs()
    orders = create_dictionary(pairs)

    print('Waiting...')
    print(orders)
    for active in MAIN_ACTIVE:
        for (currency_1, currencies_1) in orders.items():
            # print(currency_1, '--', currencies_1)
            for (currency_2, order) in currencies_1.items():
                if currency_2 == active or currency_1 == active:
                    continue
                try:
                    order_1 = orders[active][currency_1]
                except:
                    order_1 = '------'
                order_2 = order
                try:
                    order_3 = orders[currency_2][active]
                except:
                    order_3='------'
                print(order_1, '\n', order_2, '\n', order_3)

                # Формируем объем
                amount = get_amount()
                if amount != 0:
                    print('amount----', amount)
                    # позволяет понять является ли данная связка арбитражной ситуацией
                    try:
                        order_price = order_1['price'] * amount
                        print('order_price----', order_price)
                        transfer_1 = amount * (1 - COMMISSION)
                        print('transfrer_1----', transfer_1)
                        transfer_2 = transfer_1 / order_2['price'] * (1 - COMMISSION)
                        print('trasfer_2----', transfer_2)
                        transfer_3 = transfer_2 / order_3['price'] * (1 - COMMISSION)
                        print('transfer_3----', transfer_3)
                    except:
                        print('Not for us')


                    if (transfer_3 / order_price) > 1:
                        print('##############')
                        print('Find percent:', transfer_3)
                        print('Amount:', str(amount), currency_1)
                        print('Order price:', str(order_price), active)
                        print('Income:', str(transfer_3), active)
                        print('Orders:')
                        print(order_1, '=>')
                        print(order_2, '=>')
                        print(order_3)

    time.sleep(1)