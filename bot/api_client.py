# Django API bilan aloqa qiluvchi klass - barcha HTTP so'rovlar shu yerda

import aiohttp
from .bot_config import API_BASE_URL


class ApiClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None

    async def login(self, username, password):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/auth/login/", json={
                "username": username,
                "password": password
            }) as resp:
                data = await resp.json()
                if resp.status == 200:
                    self.token = data.get('access')
                return data

    def headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    async def get_subscriber_by_account(self, account_number):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/subscribers/?search={account_number}",
                headers=self.headers()
            ) as resp:
                return await resp.json()

    async def get_meters(self, subscriber_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/meters/?subscriber={subscriber_id}",
                headers=self.headers()
            ) as resp:
                return await resp.json()

    async def get_last_reading(self, meter_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/readings/?meter={meter_id}",
                headers=self.headers()
            ) as resp:
                return await resp.json()

    async def submit_reading(self, meter_id, period, value, photo_bytes, filename):
        form = aiohttp.FormData()
        form.add_field('meter', str(meter_id))
        form.add_field('period', period)
        form.add_field('value', str(value))
        form.add_field('photo', photo_bytes, filename=filename, content_type='image/jpeg')

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/readings/",
                data=form,
                headers=self.headers()
            ) as resp:
                return await resp.json()

    async def get_pending_readings(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/readings/?status=yuborilgan",
                headers=self.headers()
            ) as resp:
                return await resp.json()

    async def approve_reading(self, reading_id):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/readings/{reading_id}/approve/",
                headers=self.headers()
            ) as resp:
                return await resp.json()

    async def reject_reading(self, reading_id, reason):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/readings/{reading_id}/reject/",
                json={"reject_reason": reason},
                headers=self.headers()
            ) as resp:
                return await resp.json()

    async def get_my_invoices(self, subscriber_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/invoices/my/?subscriber={subscriber_id}",
                headers=self.headers()
            ) as resp:
                return await resp.json()


api_client = ApiClient()