def format_date(year, month_and_day_str):
    month = month_and_day_str.split("月")[0].zfill(2)
    day = month_and_day_str.split("月")[1].replace("日", "").zfill(2)

    return str(year) + month + day
