import os
import gettext
from datetime import datetime

from . import matching, scoring, time_estimates, feedback

def setup_translation(lang_code='en'):
    """Setup translation function _() for the given language code.
    
    Args:
        lang_code (str): Language code (e.g. 'en', 'zh_CN'). Defaults to 'en'.
    """
    global _  # Make _ available globally
    
    LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
    DOMAIN = 'messages'
    languages_to_try = []

    # 1. Core logic for implementing locale aliasing
    if lang_code.lower().startswith('zh'):
        # For any Chinese variants, build a fallback chain
        # For example, if lang_code is 'zh', the list will be ['zh', 'zh_CN']
        # If lang_code is 'zh_Hans_CN', list will be ['zh_Hans_CN', 'zh_CN']
        # gettext will first look for 'zh_Hans_CN', then fall back to 'zh_CN'
        languages_to_try = [lang_code, 'zh_CN', 'zh']
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
            fallback=True # fallback=True ensures no exception if all languages not found
        )
        
        # 3. Install translation function _() globally
        translation.install()
        print(f"Successfully loaded translation: {translation.info().get('language')}")

    except FileNotFoundError:
        # If even fallback language is not found, use default gettext (no translation)
        print("No suitable translation found. Falling back to original strings.")
        _ = gettext.gettext

    from .feedback import get_feedback as _get_feedback
    from . import feedback
    feedback._ = _

def zxcvbn(password, user_inputs=None, max_length=72, lang='en'):
    # Throw error if password exceeds max length
    if len(password) > max_length:
        raise ValueError(f"Password exceeds max length of {max_length} characters.")
    setup_translation(lang)

    try:
        # Python 2 string types
        basestring = (str, unicode)
    except NameError:
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
