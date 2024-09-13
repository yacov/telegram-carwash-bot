import os
from datetime import datetime, timedelta
from airtable import Airtable
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
BASE_ID = os.environ.get('BASE_ID')


__all__ = ['init_airtable_tables', 'get_today_stats', 'get_yesterday_stats', 'get_worker_data', 'update_worker_language', 'airtable_cache']

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

    # Get scans (washes) for today
    scans_formula = f"AND(IS_SAME({{Timestamp}}, '{today_str}', 'day'), IS_BEFORE({{Timestamp}}, '{tomorrow_str}'))"
    scans = scans_table.get_all(formula=scans_formula)
    
    total_washed = len(scans)
    normal_wash = sum(1 for scan in scans if not scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    additional_cleaning = sum(1 for scan in scans if scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    light_wash = sum(1 for scan in scans if not scan['fields'].get('CleanGlue') and scan['fields'].get('ReturnCleaning'))

    # Get car drying jobs for today
    dryers_formula = f"AND(IS_SAME({{Work Started}}, '{today_str}', 'day'), IS_BEFORE({{Work Started}}, '{tomorrow_str}'))"
    dryed = cardryers_table.get_all(formula=dryers_formula)
    total_dryed = len(dryed)

    # Get polishing jobs for today
    polish_formula = f"AND(IS_SAME({{Timestamp}}, '{today_str}', 'day'), IS_BEFORE({{Timestamp}}, '{tomorrow_str}'))"
    polished = polish_table.get_all(formula=polish_formula)
    total_polished = len(polished)
    full_polish = sum(1 for polish in polished if polish['fields'].get('Services') == 'FullPolish')
    half_polish = sum(1 for polish in polished if polish['fields'].get('Services') == 'HalfPolish')

    return {
        'total_washed': total_washed,
        'normal_wash': normal_wash,
        'additional_cleaning': additional_cleaning,
        'light_wash': light_wash,
        'total_dryed': total_dryed,
        'total_polished': total_polished,
        'full_polish': full_polish,
        'half_polish': half_polish
    }
async def get_yesterday_stats(airtable_tables):
    yesterday = (datetime.now() - timedelta(days=1)).date()
    day_before_yesterday = yesterday - timedelta(days=1)
    yesterday_str = yesterday.isoformat()
    day_before_yesterday_str = day_before_yesterday.isoformat()

    scans_table = airtable_tables['scans']
    cardryers_table = airtable_tables['cardryers']
    polish_table = airtable_tables['polish']

    # Get scans (washes) for yesterday
    scans_formula = f"AND(IS_SAME({{Timestamp}}, '{yesterday_str}', 'day'), IS_AFTER({{Timestamp}}, '{day_before_yesterday_str}'))"
    scans = scans_table.get_all(formula=scans_formula)
    
    total_washed = len(scans)
    normal_wash = sum(1 for scan in scans if not scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    additional_cleaning = sum(1 for scan in scans if scan['fields'].get('CleanGlue') and not scan['fields'].get('ReturnCleaning'))
    light_wash = sum(1 for scan in scans if not scan['fields'].get('CleanGlue') and scan['fields'].get('ReturnCleaning'))

    # Get polishing jobs for yesterday
    polish_formula = f"AND(IS_SAME({{Timestamp}}, '{yesterday_str}', 'day'), IS_AFTER({{Timestamp}}, '{day_before_yesterday_str}'))"
    polished = polish_table.get_all(formula=polish_formula)
    total_polished = len(polished)
    full_polish = sum(1 for polish in polished if polish['fields'].get('Services') == 'FullPolish')
    half_polish = sum(1 for polish in polished if polish['fields'].get('Services') == 'HalfPolish')

    # Calculate revenue
    revenue = (
        normal_wash * 70 +
        additional_cleaning * 75 +
        light_wash * 50 +
        full_polish * 300 +
        half_polish * 150
    )

    return {
        'total_washed': total_washed,
        'normal_wash': normal_wash,
        'additional_cleaning': additional_cleaning,
        'light_wash': light_wash,
        'total_polished': total_polished,
        'full_polish': full_polish,
        'half_polish': half_polish,
        'revenue': revenue
    }

async def get_worker_data(workers_table, user_id: int) -> dict:
    worker = workers_table.search('TelegramID', str(user_id))
    if worker:
        return worker[0]['fields']
    return None

async def update_worker_language(workers_table, user_id: int, language: str):
    worker = workers_table.search('TelegramID', str(user_id))
    if worker:
        workers_table.update(worker[0]['id'], {'Language': language})