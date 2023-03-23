# import aiohttp
# import asyncio
# from datetime import datetime, timedelta
# import platform
#
#
# class PrivatBankAPI:
#     BASE_URL = 'https://api.privatbank.ua/p24api/exchange_rates'
#
#     async def get_exchange_rates(self, currency: str, days: int) -> dict:
#         """Отримати курс валюти за останні кілька днів."""
#         end_date = datetime.now()
#         start_date = end_date - timedelta(days=days)
#
#         async with aiohttp.ClientSession() as session:
#             response = await session.get(
#                 f'{self.BASE_URL}?json&date={start_date.strftime("%d.%m.%Y")}'
#             )
#             data = await response.json()
#
#         exchange_rates = []
#         for rate in data['exchangeRate']:
#             if rate['currency'] == currency:
#                 rate_date = datetime.strptime(rate['date'], '%d.%m.%Y').date()
#                 if start_date <= rate_date <= end_date:
#                     exchange_rates.append({
#                         'date': rate_date,
#                         'buy_rate': rate['purchaseRate'],
#                         'sale_rate': rate['saleRate']
#                     })
#
#         return exchange_rates
#
#
# async def main():
#     api = PrivatBankAPI()
#
#     try:
#         days = int(input("Enter number of days (not more than 10): "))
#         if days <= 0 or days > 10:
#             raise ValueError
#     except ValueError:
#         print("Invalid number of days.")
#         return
#
#     print("Exchange rates for USD:")
#     rates_usd = await api.get_exchange_rates('USD', days)
#     for rate in rates_usd:
#         print(f"{rate['date'].strftime('%Y-%m-%d')}: buy - {rate['buy_rate']}, sale - {rate['sale_rate']}")
#
#     print("Exchange rates for EUR:")
#     rates_eur = await api.get_exchange_rates('EUR', days)
#     for rate in rates_eur:
#         print(f"{rate['date'].strftime('%Y-%m-%d')}: buy - {rate['buy_rate']}, sale - {rate['sale_rate']}")
#
#
# if __name__ == '__main__':
#     if platform.system() == 'Windows':
#         asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#     asyncio.run(main())
# #
import json

import aiohttp
import asyncio
import platform
from datetime import datetime, timedelta


# async def request(url: str):
#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.get(url) as resp:
#                 if resp.status == 200:
#                     result = await resp.json()
#                     return result
#                 else:
#                     print(f"Error status: {resp.status} for {url}")
#         except aiohttp.ClientConnectorError as err:
#             print(f'Connection error: {url}', str(err))


def get_days_from_input() -> int:
    try:
        days = int(input("Enter number of days (less than 10): "))
        if days <= 0 or days > 10:
            raise ValueError
    except ValueError:
        print("Invalid number of days. We will show data only for today")
        days = 1

    return int(days)

def get_urls(days: int):
    url_list = []
    today = datetime.now()
    for i in range(0, days):
        date = (today - timedelta(days=i)).strftime('%d.%m.%Y')
        url_list.append(f"https://api.privatbank.ua/p24api/exchange_rates?date={date}")
    return url_list

async def request(url):
    async with aiohttp.ClientSession() as session:
        ex_rates_dicts = {}
        currency_list = ['USD', 'EUR']

        try:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Error status: {response.status} for {url}")
                    return None

                res = await response.json()

                for i in res['exchangeRate']:
                    if i['currency'] in currency_list:
                        if res['date'] not in ex_rates_dicts:
                            ex_rates_dicts[res['date']] = {}
                        ex_rates_dicts[res['date']][i['currency']] = {'sale': i['saleRateNB'], 'purchase': i['purchaseRateNB']}

        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))

        return ex_rates_dicts

async def main(days):
    urls = get_urls(days)

    tasks = []
    for url in urls:
        tasks.append(request(url))

    result = {}
    [result.update(task_result) for task_result in await asyncio.gather(*tasks)]

    print(json.dumps(result, indent=4))

if __name__ == '__main__':
    days = get_days_from_input()

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main(days))

