import os
from datetime import datetime
import gettext
import threading
from . import matching, scoring, time_estimates, feedback
from .zxcvbn_class import ZxcvbnInstance


# Global variable to track the last language code for which translation was set up
_LAST_LANG_CODE_SETUP = None

_THREAD_SAFE = False
_LOCK = threading.Lock()

def set_thread_safe(enabled=True):
    """
    Configures the thread-safety mode for dictionary loading.
    Note: This only affects dictionary loading operations in matching.py.
    
    Args:
        enabled (bool): When True, enables thread-safe lazy loading of dictionaries.
                      Defaults to True.
    """
    global _THREAD_SAFE
    _THREAD_SAFE = enabled

def setup_translation(lang_code='en_US'):
    """Setup translation function _() for the given language code.
    
    Args:
        lang_code (str): Language code (e.g. 'en', 'zh_Hans'). Defaults to 'en'.
    """
    global _  # Make _ available globally
    global _LAST_LANG_CODE_SETUP

    # Only set up translation if the language code has changed
    if lang_code == _LAST_LANG_CODE_SETUP:
        return

    LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
    DOMAIN = 'messages'
    languages_to_try = []

    # 1. Core logic for implementing locale aliasing
    if lang_code.lower().startswith('zh'):
        # For any Chinese variants, build a fallback chain
        languages_to_try = [lang_code, 'zh_Hans']
        # Remove duplicates while preserving order
        languages_to_try = sorted(set(languages_to_try), key=languages_to_try.index)
    else:
        # For other languages, use directly
        languages_to_try = [lang_code]

    print(f"Attempting to load translations for '{lang_code}'. Search path: {languages_to_try}")
    
    try:
        # 2. Pass our constructed language list to gettext
        translation = gettext.translation(
            DOMAIN,
            localedir=LOCALE_DIR, 
            languages=languages_to_try,
            fallback=True
        )
        
        # Get detailed info about the loaded translation
        actual_lang = translation.info().get('language')
        matched_lang = actual_lang if actual_lang else 'en-us'  # fallback
        print(f"Loaded translation. Requested: {languages_to_try} | Actual: {actual_lang} | Using: {matched_lang}")
        
        # 3. Install translation function _() globally
        translation.install()
        # Update the last configured language code with the matched code
        _LAST_LANG_CODE_SETUP = matched_lang

    except FileNotFoundError:
        # If even fallback language is not found, use default gettext (no translation)
        print("No suitable translation found. Falling back to original strings.")
        _ = gettext.gettext

    from .feedback import get_feedback as _get_feedback
    from . import feedback
    feedback._ = _



def zxcvbn(password, user_inputs=None, max_length=72, lang='en', thread_safe=False):
    # Throw error if password exceeds max length
    if len(password) > max_length:
        raise ValueError(f"Password exceeds max length of {max_length} characters.")
    set_thread_safe(thread_safe)
    setup_translation(lang)
    # Python 2/3 compatibility for string types
    import sys
    if sys.version_info[0] == 2:
        # Python 2 string types
        basestring = (str, unicode)
    else:
        # Python 3 string types
        basestring = (str, bytes)

    if user_inputs is None:
        user_inputs = []

    start = datetime.now()

    sanitized_inputs = []
    for arg in user_inputs:
        if not isinstance(arg, basestring):
            arg = str(arg)
        sanitized_inputs.append(arg.lower())

    matches = matching.omnimatch(password, user_inputs=sanitized_inputs)
    result = scoring.most_guessable_match_sequence(password, matches)
    result['calc_time'] = datetime.now() - start

    attack_times = time_estimates.estimate_attack_times(result['guesses'])
    for prop, val in attack_times.items():
        result[prop] = val

    result['feedback'] = feedback.get_feedback(result['score'],
                                               result['sequence'])

    return result
