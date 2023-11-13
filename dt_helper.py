from datetime import datetime, timedelta

def format_dt_diff(dt):
    # there seems to be a delay between sql/python
    # 10 seconds seems fine for user interaction
    time_difference = now = datetime.now() - dt + timedelta(seconds=10)
    
    '''
        under a min show seconds
        under hour show mins
        under day show hours / mins
        >= day show date & time
    '''
    
    if time_difference < timedelta(minutes=1):
        result = f"{time_difference.seconds} seconds ago"
    elif time_difference < timedelta(hours=1):
        result = f"{time_difference.seconds // 60} minutes ago"
    elif time_difference < timedelta(days=1):
        secs_per_hour = 60*60
        hours = time_difference.seconds // secs_per_hour
        minutes = (time_difference.seconds % secs_per_hour) // 60
        result = f"{hours} hours {minutes} minutes ago"
    else:
        result = dt.strftime('%m/%d/%y %I:%M %p')
        
    return result