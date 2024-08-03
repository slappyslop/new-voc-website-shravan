import datetime

def get_end_date(today):
    """
    Evaluates the custom VOC membership end date logic
    
    If today is between Jan 1 and Apr 30 inclusive, return Sept 30 of the current year
    Otherwise return Sept 30 of the following year
    """
    current_year = today.year
    
    if datetime.datetime(current_year, 1, 1) <= today <= datetime.datetime(current_year, 4, 30):
        return datetime.datetime(current_year, 9, 30)
    
    else:
        return datetime.datetime(current_year + 1, 9, 30)