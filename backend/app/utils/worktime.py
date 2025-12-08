from datetime import date, datetime, timedelta

# 可在此维护法定节假日与调休工作日
SPECIAL_HOLIDAYS = set()
SPECIAL_WORKDAYS = set()

def is_workday(d: date) -> bool:
    if d in SPECIAL_HOLIDAYS:
        return False
    if d in SPECIAL_WORKDAYS:
        return True
    # 周一至周五为工作日
    return d.weekday() < 5

def count_workdays(start: date, end: date) -> int:
    if not start or not end:
        return 0
    if end < start:
        return 0
    cur = start
    days = 0
    while cur <= end:
        if is_workday(cur):
            days += 1
        cur += timedelta(days=1)
    return days

def compute_estimated_hours(start: date, end: date) -> float:
    return float(count_workdays(start, end) * 8)

def compute_actual_hours(start: date, completed_at: datetime) -> float:
    if not start or not completed_at:
        return 0.0
    end_date = completed_at.date()
    return float(count_workdays(start, end_date) * 8)
