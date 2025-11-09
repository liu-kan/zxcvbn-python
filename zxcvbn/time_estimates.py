from decimal import Decimal, Context, Inexact
from gettext import gettext as _, ngettext

def estimate_attack_times(guesses):
    crack_times_seconds = {
        'online_throttling_100_per_hour': Decimal(guesses) / float_to_decimal(100.0 / 3600.0),
        'online_no_throttling_10_per_second': Decimal(guesses) / float_to_decimal(10.0),
        'offline_slow_hashing_1e4_per_second': Decimal(guesses) / float_to_decimal(1e4),
        'offline_fast_hashing_1e10_per_second': Decimal(guesses) / float_to_decimal(1e10),
    }

    crack_times_display = {}
    for scenario, seconds in crack_times_seconds.items():
        crack_times_display[scenario] = display_time(seconds)

    return {
        'crack_times_seconds': crack_times_seconds,
        'crack_times_display': crack_times_display,
        'score': guesses_to_score(guesses),
    }


def guesses_to_score(guesses):
    delta = 5

    if guesses < 1e3 + delta:
        # risky password: "too guessable"
        return 0
    elif guesses < 1e6 + delta:
        # modest protection from throttled online attacks: "very guessable"
        return 1
    elif guesses < 1e8 + delta:
        # modest protection from unthrottled online attacks: "somewhat
        # guessable"
        return 2
    elif guesses < 1e10 + delta:
        # modest protection from offline attacks: "safely unguessable"
        # assuming a salted, slow hash function like bcrypt, scrypt, PBKDF2,
        # argon, etc
        return 3
    else:
        # strong protection from offline attacks under same scenario: "very
        # unguessable"
        return 4


def display_time(seconds):
    minute = 60
    hour = minute * 60
    day = hour * 24
    month = day * 31
    year = month * 12
    century = year * 100
    if seconds < 1:
        return _('less than a second')
    elif seconds < minute:
        base = int(round(seconds))
        return ngettext('%s second', '%s seconds', base) % base
    elif seconds < hour:
        base = int(round(seconds / minute))
        return ngettext('%s minute', '%s minutes', base) % base
    elif seconds < day:
        base = int(round(seconds / hour))
        return ngettext('%s hour', '%s hours', base) % base
    elif seconds < month:
        base = int(round(seconds / day))
        return ngettext('%s day', '%s days', base) % base
    elif seconds < year:
        base = int(round(seconds / month))
        return ngettext('%s month', '%s months', base) % base
    elif seconds < century:
        base = int(round(seconds / year))
        return ngettext('%s year', '%s years', base) % base
    else:
        return _('centuries')

def float_to_decimal(f):
    "Convert a floating point number to a Decimal with no loss of information"
    n, d = f.as_integer_ratio()
    numerator, denominator = Decimal(n), Decimal(d)
    ctx = Context(prec=60)
    result = ctx.divide(numerator, denominator)
    while ctx.flags[Inexact]:
        ctx.flags[Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)
    return result
