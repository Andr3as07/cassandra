import time

def sec2human(sec):
    hours = sec // (60 * 60)
    sec = sec % (60 * 60)

    m = sec // 60
    sec = sec % 60

    if hours > 0:
        return str(hours) + "h " + str(m) + "min "
    elif m > 0:
        return str(m) + "min " + str(sec) + "sec"
    else:
        return str(sec) + "sec"

def getts():
    return int(time.time())
