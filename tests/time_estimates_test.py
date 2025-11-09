import gettext
import sys
from pathlib import Path

import zxcvbn.time_estimates as time_estimates
from zxcvbn.time_estimates import estimate_attack_times

def test_long_ints_dont_overflow():
    try:
        long_guesses = sys.maxsize + 1
    except expression as identifier:
        long_guesses = sys.maxint + 1

    attack_times = estimate_attack_times(long_guesses)
    assert 'crack_times_seconds' in attack_times
    assert 'crack_times_display' in attack_times
    assert 'score' in attack_times


def test_crack_times_display_uses_localized_strings():
    # time_estimates binds gettext functions during import, so tests must
    # override them directly to simulate a different locale.
    locale_dir = Path(__file__).resolve().parents[1] / 'zxcvbn' / 'locale'
    zh_translation = gettext.translation(
        'messages', localedir=str(locale_dir), languages=['zh_Hans']
    )

    original_gettext = time_estimates._
    original_ngettext = time_estimates.ngettext
    try:
        time_estimates._ = zh_translation.gettext
        time_estimates.ngettext = zh_translation.ngettext
        attack_times = time_estimates.estimate_attack_times(1)
    finally:
        time_estimates._ = original_gettext
        time_estimates.ngettext = original_ngettext

    display = attack_times['crack_times_display']['offline_fast_hashing_1e10_per_second']
    assert display == '不到一秒'
