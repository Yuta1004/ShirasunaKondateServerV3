def format_date(year, month_and_day_str):
    month = month_and_day_str.split("月")[0].zfill(2)
    day = month_and_day_str.split("月")[1].replace("日", "").zfill(2)

    return str(year) + month + day


# 西暦を和暦表記にする関数
def christian_to_japanese(christian_era, month):
    japanese_calendar_dict = {
        "HEISEI": "h",
        "HEISEI_NO_TSUGI": "a"
    }

    if christian_era < 1989:
        raise ValueError("平成時代以上に対応しています．(1989年~)")

    if 1989 <= christian_era < 2019:
        japanese_date = japanese_calendar_dict["HEISEI"] + str(christian_era - 1988)
    elif christian_era == 2019:
        if month <= 4:
            japanese_date = japanese_calendar_dict["HEISEI"] + str(christian_era - 1988)
        else:
            japanese_date = japanese_calendar_dict["HEISEI_NO_TSUGI"] + str(christian_era - 2018)
    else:
        japanese_date = japanese_calendar_dict["HEISEI_NO_TSUGI"] + str(christian_era - 2018)

    return japanese_date


def list_to_plaintext(arg_list, splitter=";"):
    plaintext = ""
    for item in arg_list:
        plaintext += item + splitter

    return plaintext
