import os
from datetime import datetime, timedelta
from airtable import Airtable
from dotenv import load_dotenv
from utils import calculate_revenue
from cache import monthly_stats_cache

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('BASE_ID')

__all__ = ['init_airtable_tables', 'get_today_stats', 'get_yesterday_stats', 'get_worker_data', 'update_worker_language']

def init_airtable_tables():
    return {
        'scans': Airtable(BASE_ID, 'Scans', api_key=AIRTABLE_API_KEY),
        'cardryers': Airtable(BASE_ID, 'CarDryers', api_key=AIRTABLE_API_KEY),
        'polish': Airtable(BASE_ID, 'Polish', api_key=AIRTABLE_API_KEY),
        'workers': Airtable(BASE_ID, 'Workers', api_key=AIRTABLE_API_KEY)
    }

async def get_today_stats(airtable_tables):
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    today_str = today.isoformat()
    tomorrow_str = tomorrow.isoformat()

    scans_table = airtable_tables['scans']
    cardryers_table = airtable_tables['cardryers']
    polish_table = airtable_tables['polish']

    scans_formula = f"AND(IS_AFTER({{Timestamp}}, '{today_str}'), IS_BEFORE({{Timestamp}}, '{tomorrow_str}'))"
    scans_records = scans_table.get_all(formula=scans_formula)

    polish_formula = f"AND(IS_AFTER({{Timestamp}}, '{today_str}'), IS_BEFORE({{Timestamp}}, '{tomorrow_str}'))"
    polish_records = polish_table.get_all(formula=polish_formula)

    dryers_formula = f"AND(IS_AFTER({{Work Started}}, '{today_str}'), IS_BEFORE({{Work Started}}, '{tomorrow_str}'))"
    dryed = cardryers_table.get_all(formula=dryers_formula)

    total_washed = len(scans_records)
    normal_wash = sum(1 for scan in scans_records if not scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    additional_cleaning = sum(1 for scan in scans_records if scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    light_wash = sum(1 for scan in scans_records if not scan['fields'].get('CleanGlue') and scan['fields'].get('ReturnCleaning'))

    total_polished = len(polish_records)
    full_polish = sum(1 for polish in polish_records if polish['fields'].get('Services') == 'FullPolish')
    half_polish = sum(1 for polish in polish_records if polish['fields'].get('Services') == 'HalfPolish')
    shlaif = sum(1 for polish in polish_records if polish['fields'].get('Services') == 'Shlaif')

    wash_revenue = calculate_revenue(scans_records)
    polish_revenue = sum(
        350 if polish['fields'].get('Services') == 'FullPolish' else
        150 if polish['fields'].get('Services') == 'HalfPolish' else
        1000 if polish['fields'].get('Services') == 'Shlaif' else
        0 for polish in polish_records
    )
    total_revenue = wash_revenue + polish_revenue

    return {
        'total_washed': total_washed,
        'normal_wash': normal_wash,
        'additional_cleaning': additional_cleaning,
        'light_wash': light_wash,
        'total_polished': total_polished,
        'full_polish': full_polish,
        'half_polish': half_polish,
        'shlaif': shlaif,
        'wash_revenue': wash_revenue,
        'polish_revenue': polish_revenue,
        'total_revenue': total_revenue,
        'total_dryed': len(dryed),
    }

async def get_yesterday_stats(airtable_tables):
    yesterday = (datetime.now() - timedelta(days=1)).date()
    day_before_yesterday = yesterday - timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    day_before_yesterday_str = day_before_yesterday.isoformat()

    scans_table = airtable_tables['scans']
    polish_table = airtable_tables['polish']

    scans_formula = f"AND(IS_AFTER({{Timestamp}}, '{yesterday_str}'), IS_BEFORE({{Timestamp}}, '{day_before_yesterday_str}'))"
    scans = scans_table.get_all(formula=scans_formula)

    polish_formula = f"AND(IS_AFTER({{Timestamp}}, '{yesterday_str}'), IS_BEFORE({{Timestamp}}, '{day_before_yesterday_str}'))"
    polished = polish_table.get_all(formula=polish_formula)

    total_washed = len(scans)
    normal_wash = sum(1 for scan in scans if not scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    additional_cleaning = sum(1 for scan in scans if scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    light_wash = sum(1 for scan in scans if not scan['fields'].get('CleanGlue') and scan['fields'].get('ReturnCleaning'))

    total_polished = len(polished)
    full_polish = sum(1 for polish in polished if polish['fields'].get('Services') == 'FullPolish')
    half_polish = sum(1 for polish in polished if polish['fields'].get('Services') == 'HalfPolish')
    shlaif = sum(1 for polish in polished if polish['fields'].get('Services') == 'Shlaif')

    revenue = calculate_revenue(scans) + sum(
        145 if polish['fields'].get('Services') == 'FullPolish' else
        75 if polish['fields'].get('Services') == 'HalfPolish' else
        1000 if polish['fields'].get('Services') == 'Shlaif' else
        0 for polish in polished
    )

    return {
        'total_washed': total_washed,
        'normal_wash': normal_wash,
        'additional_cleaning': additional_cleaning,
        'light_wash': light_wash,
        'total_polished': total_polished,
        'full_polish': full_polish,
        'half_polish': half_polish,
        'shlaif': shlaif,
        'revenue': revenue
    }

async def get_worker_data(workers_table, user_id: int) -> dict:
    worker = workers_table.search('TelegramID', str(user_id))
    return worker[0]['fields'] if worker else None

async def update_worker_language(workers_table, user_id: int, language: str):
    worker = workers_table.search('TelegramID', str(user_id))
    if worker:
        workers_table.update(worker[0]['id'], {'Language': language})

async def get_monthly_stats(airtable_tables):
    return await monthly_stats_cache.get_stats(airtable_tables)

