def strfduration(duration, _format="HH:mm:ss"):
    seconds = duration.seconds
    microseconds = duration.microseconds

    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60

    days = duration.days
    hours_days = hours + (days * 24)

    format_map = {
        'dd': f'{days:02d}',            'd': str(days),
        'HH': f'{hours_days:02d}',      'H': str(hours_days),
        'hh': f'{hours:02d}',           'h': str(hours),
        'mm': f'{minutes:02d}',         'm': str(minutes),
        'ss': f'{seconds:02d}',         's': str(seconds),
        'uu': f'{microseconds:02d}',    'u': str(microseconds),
    }

    string = _format
    for k,v in format_map.items():
        if k in _format:
            string = string.replace(k,v)

    return string