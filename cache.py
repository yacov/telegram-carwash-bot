from datetime import datetime, timedelta
from utils import calculate_revenue, get_workdays_in_period
from datetime import datetime, timedelta

from utils import calculate_revenue, get_workdays_in_period


class MonthlyStatsCache:
    def __init__(self):
        self._cache = {}
        self._last_update = None

    async def get_stats(self, airtable_tables, force_refresh=False):
        current_date = datetime.now().date()
        if force_refresh or self._last_update != current_date:
            self._cache = await self.get_monthly_stats_raw(airtable_tables)
            self._last_update = current_date
        return self._cache

    async def update_daily(self, context):
        airtable_tables = context.job.data['airtable_tables']
        await self.get_stats(airtable_tables, force_refresh=True)

    async def get_monthly_stats_raw(self, airtable_tables):
        today = datetime.now().date()
        month_start = today.replace(day=1)
        yesterday = today - timedelta(days=1)
        total_goal = 2500  # Monthly goal for total washed cars

        scans_table = airtable_tables['scans']
        polish_table = airtable_tables['polish']

        # Fetch records from the start of the month up to yesterday
        scans_filter = f"AND(IS_AFTER({{Timestamp}}, '{month_start.isoformat()}'), IS_BEFORE({{Timestamp}}, '{today.isoformat()}'))"
        scans_records = scans_table.get_all(formula=scans_filter)

        polish_filter = f"AND(IS_AFTER({{Timestamp}}, '{month_start.isoformat()}'), IS_BEFORE({{Timestamp}}, '{today.isoformat()}'))"
        polish_records = polish_table.get_all(formula=polish_filter)

        # Calculate statistics
        workdays_passed = get_workdays_in_period(month_start, yesterday)
        total_workdays = get_workdays_in_period(month_start, self._get_last_day_of_month(today))
        daily_goal = total_goal / total_workdays if total_workdays > 0 else total_goal
        current_target = daily_goal * workdays_passed

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
            145 if polish['fields'].get('Services') == 'FullPolish' else
            75 if polish['fields'].get('Services') == 'HalfPolish' else
            50 for polish in polish_records
        )
        total_revenue = wash_revenue + polish_revenue

        deviation = total_washed - current_target
        remaining_workdays = max(total_workdays - workdays_passed, 0)
        cars_needed = max(total_goal - total_washed, 0)
        required_daily_cars = cars_needed / remaining_workdays if remaining_workdays > 0 else float('inf')

        on_track = total_washed >= current_target
        progress_symbol = "🟢" if on_track else "🔴"

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
            'progress_symbol': progress_symbol,
            'on_track': on_track,
            'total_goal': total_goal,
            'current_target': int(current_target),
            'workdays_passed': workdays_passed,
            'total_workdays': total_workdays,
            'deviation': int(deviation),
            'remaining_workdays': remaining_workdays,
            'required_daily_cars': int(required_daily_cars)
        }

    def _get_last_day_of_month(self, any_day):
        next_month = any_day.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

monthly_stats_cache = MonthlyStatsCache()
