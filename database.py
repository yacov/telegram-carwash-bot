import os
from datetime import datetime, timedelta
from airtable import Airtable
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('BASE_ID')

class AirtableCache:
    def __init__(self, expiration_minutes=5):
        self.cache = {}
        self.expiration_minutes = expiration_minutes

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(minutes=self.expiration_minutes):
                return data
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

airtable_cache = AirtableCache()

def init_airtable_tables():
    return {
        'scans': Airtable(BASE_ID, 'Scans', api_key=AIRTABLE_API_KEY),
        'cardryers': Airtable(BASE_ID, 'CarDryers', api_key=AIRTABLE_API_KEY),
        'polish': Airtable(BASE_ID, 'Polish', api_key=AIRTABLE_API_KEY),
        'workers': Airtable(BASE_ID, 'Workers', api_key=AIRTABLE_API_KEY)
    }

async def get_today_stats(scans_table):
    cached_stats = airtable_cache.get('today_stats')
    if cached_stats:
        return cached_stats

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    formula = f"AND(IS_SAME({{Timestamp}}, '{today}', 'day'), IS_BEFORE({{Timestamp}}, '{tomorrow}'))"
    all_records = scans_table.get_all(formula=formula)

    stats = {
        'total_washed': 0,
        'normal_wash': 0,
        'additional_cleaning': 0,
        'light_wash': 0,
        'total_dryed': 0,
        'total_polished': 0,
        'full_polish': 0,
        'half_polish': 0
    }

    for record in all_records:
        fields = record['fields']
        if 'Type' not in fields:
            continue

        if fields['Type'] == 'Wash':
            stats['total_washed'] += 1
            if fields.get('CleanGlue') and not fields.get('ReturnCleaning'):
                stats['additional_cleaning'] += 1
            elif not fields.get('CleanGlue') and fields.get('ReturnCleaning'):
                stats['light_wash'] += 1
            else:
                stats['normal_wash'] += 1
        elif fields['Type'] == 'Dry':
            stats['total_dryed'] += 1
        elif fields['Type'] == 'Polish':
            stats['total_polished'] += 1
            if fields.get('Services') == 'FullPolish':
                stats['full_polish'] += 1
            elif fields.get('Services') == 'HalfPolish':
                stats['half_polish'] += 1

    airtable_cache.set('today_stats', stats)
    return stats

async def get_worker_data(workers_table, user_id: int) -> dict:
    worker = workers_table.search('TelegramID', str(user_id))
    if worker:
        return worker[0]['fields']
    return None

async def update_worker_language(workers_table, user_id: int, language: str):
    worker = workers_table.search('TelegramID', str(user_id))
    if worker:
        workers_table.update(worker[0]['id'], {'Language': language})