import json
import aiohttp
import asyncio
import platform
from datetime import datetime, timedelta

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

