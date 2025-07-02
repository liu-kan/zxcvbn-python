# -*- coding: utf-8 -*-
import os
import threading
from datetime import datetime
import gettext
from . import matching, scoring, time_estimates, feedback


class ZxcvbnInstance:
    """
    Thread-safe zxcvbn password strength estimator instance.
    
    This class maintains dictionaries and translations in memory to avoid
    repeated loading, and allows password re-evaluation after modification.
    """
    
    def __init__(self, lang='en', user_inputs=None, max_length=72, thread_safe=True):
        """
        Initialize a zxcvbn instance with persistent dictionaries and translations.
        
        Args:
            lang (str): Language code for translations (e.g. 'en', 'zh_CN')
            user_inputs (list): List of user-specific inputs to include in dictionary
            max_length (int): Maximum password length to evaluate
            thread_safe (bool): Enable thread-safe operations
        """
        self._lock = threading.RLock() if thread_safe else None
        self._thread_safe = thread_safe
        self._lang = lang
        self._max_length = max_length
        self._user_inputs = user_inputs or []
        
        # Cached data
        self._ranked_dictionaries = None
        self._translation_func = None
        self._password = None
        self._last_result = None
        
        # Initialize dictionaries and translation
        self._initialize()
    
    def _initialize(self):
        """Initialize dictionaries and translation function."""
        if self._thread_safe:
            with self._lock:
                self._load_dictionaries()
                self._setup_translation()
        else:
            self._load_dictionaries()
            self._setup_translation()
    
    def _load_dictionaries(self):
        """Load and cache ranked dictionaries."""
        if self._ranked_dictionaries is not None:
            return
            
        from .frequency_lists import FREQUENCY_LISTS
        
        # Build ranked dictionaries
        temp_dict = {}
        for name, lst in FREQUENCY_LISTS.items():
            temp_dict[name] = {word: idx for idx, word in enumerate(lst, 1)}
        
        # Add user inputs if provided
        if self._user_inputs:
            sanitized_inputs = []
            for arg in self._user_inputs:
                if not isinstance(arg, (str, bytes)):
                    arg = str(arg)
                sanitized_inputs.append(arg.lower())
            temp_dict['user_inputs'] = {word: idx for idx, word in enumerate(sanitized_inputs, 1)}
        
        self._ranked_dictionaries = temp_dict
    
    def _setup_translation(self):
        """Setup translation function for the configured language."""
        if self._translation_func is not None:
            return
            
        LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
        DOMAIN = 'messages'
        languages_to_try = []

        # Core logic for implementing locale aliasing
        if self._lang.lower().startswith('zh'):
            # For any Chinese variants, build a fallback chain
            languages_to_try = [self._lang, 'zh_CN', 'zh']
            # Remove duplicates while preserving order
            languages_to_try = sorted(set(languages_to_try), key=languages_to_try.index)
        else:
            # For other languages, use directly
            languages_to_try = [self._lang]

        try:
            # Pass our constructed language list to gettext
            translation = gettext.translation(
                DOMAIN,
                localedir=LOCALE_DIR,
                languages=languages_to_try,
                fallback=True  # fallback=True ensures no exception if all languages not found
            )
            
            self._translation_func = translation.gettext
            
        except FileNotFoundError:
            # If even fallback language is not found, use default gettext (no translation)
            self._translation_func = gettext.gettext
        
        # Update feedback module's translation function
        feedback._ = self._translation_func
    
    def set_password(self, password):
        """
        Set or update the password to be evaluated.
        
        Args:
            password (str): The password to evaluate
            
        Returns:
            dict: Password strength evaluation result
            
        Raises:
            ValueError: If password exceeds max_length
        """
        if len(password) > self._max_length:
            raise ValueError(f"Password exceeds max length of {self._max_length} characters.")
        
        if self._thread_safe:
            with self._lock:
                return self._evaluate_password(password)
        else:
            return self._evaluate_password(password)
    
    def _evaluate_password(self, password):
        """Internal method to evaluate password strength."""
        self._password = password
        
        start = datetime.now()
        
        # Prepare user inputs for this evaluation
        sanitized_inputs = []
        for arg in self._user_inputs:
            if not isinstance(arg, (str, bytes)):
                arg = str(arg)
            sanitized_inputs.append(arg.lower())
        
        # Get matches using our cached dictionaries
        matches = self._omnimatch(password, sanitized_inputs)
        result = scoring.most_guessable_match_sequence(password, matches)
        result['calc_time'] = datetime.now() - start

        attack_times = time_estimates.estimate_attack_times(result['guesses'])
        for prop, val in attack_times.items():
            result[prop] = val

        result['feedback'] = feedback.get_feedback(result['score'], result['sequence'])
        
        self._last_result = result
        return result
    
    def _omnimatch(self, password, user_inputs):
        """
        Perform all matches using cached dictionaries.
        This is a simplified version of matching.omnimatch that uses our cached data.
        """
        # Create a copy of our dictionaries for this evaluation
        ranked_dicts = dict(self._ranked_dictionaries)
        
        # Add user inputs for this specific evaluation (merge with existing user_inputs)
        if user_inputs:
            # If we already have user_inputs in our cached dictionaries, merge them
            existing_user_inputs = ranked_dicts.get('user_inputs', {})
            new_user_inputs = {word: idx for idx, word in enumerate(user_inputs, len(existing_user_inputs) + 1)}
            existing_user_inputs.update(new_user_inputs)
            ranked_dicts['user_inputs'] = existing_user_inputs
        
        matches = []
        
        # Use the existing matchers from matching module, but pass our cached dictionaries
        for matcher_name in ['dictionary_match', 'reverse_dictionary_match', 'l33t_match',
                           'spatial_match', 'repeat_match', 'sequence_match', 
                           'regex_match', 'date_match']:
            matcher = getattr(matching, matcher_name)
            matches.extend(matcher(password, _ranked_dictionaries=ranked_dicts))

        return sorted(matches, key=lambda x: (x['i'], x['j']))
    
    def get_result(self):
        """
        Get the last evaluation result.
        
        Returns:
            dict: Last password evaluation result, or None if no password has been set
        """
        if self._thread_safe:
            with self._lock:
                return self._last_result
        else:
            return self._last_result
    
    def get_password(self):
        """
        Get the current password.
        
        Returns:
            str: Current password, or None if no password has been set
        """
        if self._thread_safe:
            with self._lock:
                return self._password
        else:
            return self._password
    
    def update_user_inputs(self, user_inputs):
        """
        Update user inputs and reload dictionaries.
        
        Args:
            user_inputs (list): New list of user-specific inputs
        """
        if self._thread_safe:
            with self._lock:
                self._user_inputs = user_inputs or []
                # Force reload of dictionaries with new user inputs
                self._ranked_dictionaries = None
                self._load_dictionaries()
                # Re-evaluate current password if one is set
                if self._password is not None:
                    self._evaluate_password(self._password)
        else:
            self._user_inputs = user_inputs or []
            # Force reload of dictionaries with new user inputs
            self._ranked_dictionaries = None
            self._load_dictionaries()
            # Re-evaluate current password if one is set
            if self._password is not None:
                self._evaluate_password(self._password)
    
    def set_language(self, lang):
        """
        Change the language and reload translations.
        
        Args:
            lang (str): New language code
        """
        if self._lang == lang or (lang=='' and self._lang =='en') or (lang=='en' and self._lang ==''):
            return
        if self._thread_safe:
            with self._lock:
                self._lang = lang
                # Force reload of translation
                self._translation_func = None
                self._setup_translation()
                # Re-evaluate current password if one is set to get updated feedback
                if self._password is not None:
                    self._evaluate_password(self._password)
        else:
            self._lang = lang
            # Force reload of translation
            self._translation_func = None
            self._setup_translation()
            # Re-evaluate current password if one is set to get updated feedback
            if self._password is not None:
                self._evaluate_password(self._password)
    
    def __repr__(self):
        """String representation of the instance."""
        return f"ZxcvbnInstance(lang='{self._lang}', thread_safe={self._thread_safe}, password_set={self._password is not None})"
