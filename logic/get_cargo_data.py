import aiohttp
import asyncio

url = "https://www.0766cargo.com/logistics/getOne?waybillNumber={0}"

async def get_data(id):
    async with aiohttp.ClientSession() as session:
        async with session.get(url.format(id)) as response:
            if response.status == 200:
                return await response.json()  # Асинхронно парсим JSON
            else:
                return {"error": f"Request failed with status code {response.status}"}

