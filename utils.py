import datetime

JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

# サマータイムとウィンタータイムの開始時刻を求める関数
def summer_start(year):
    # 3月第2日曜日からサマータイム開始
    tgt_day = datetime.datetime(year, 3, 8, 0, 0, tzinfo=JST)
    move_day = 6 - tgt_day.weekday()
    tgt_day = tgt_day + datetime.timedelta(days=move_day) + datetime.timedelta(hours=3)
    return tgt_day

def winter_start(year):
    # 11月第1日曜日からウィンタータイム開始
    tgt_day = datetime.datetime(year, 11, 1, 0, 0, tzinfo=JST)
    move_day = 6 - tgt_day.weekday()
    tgt_day = tgt_day + datetime.timedelta(days=move_day) + datetime.timedelta(hours=1)
    return tgt_day

# サマータイム中かどうかを判定する関数
def is_summer_time(now=None):
    if now is None:
        now = datetime.datetime.now(tz=JST)
    ss = summer_start(now.year)
    ws = winter_start(now.year)
    return ss <= now < ws


def get_one_pips(instrument):
    if 'JPY' in instrument:
        return 0.01
    else:
        return 0.0001
