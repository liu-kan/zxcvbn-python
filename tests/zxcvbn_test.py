# -*- coding: utf-8 -*-
import pytest
from zxcvbn import zxcvbn


def test_unicode_user_inputs():
    # test Issue #12 -- don't raise a UnicodeError with unicode user_inputs or
    # passwords.
    input_ = u'Фамилия'
    password = u'pÄssword junkiË'

    zxcvbn(password, user_inputs=[input_])


def test_invalid_user_inputs():
    # don't raise an error with non-string types for user_inputs
    input_ = None
    password = u'pÄssword junkiË'

    zxcvbn(password, user_inputs=[input_])


def test_long_password():
    input_ = None
    password = "weopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioejiojweopiopdsjmkldjvoisdjfioej"

    zxcvbn(password, user_inputs=[input_], max_length=316)


def test_dictionary_password():
    # return the correct error message for a english match
    input_ = None
    password = "musculature"

    result = zxcvbn(password, user_inputs=[input_])

    assert result["feedback"]["warning"] == \
           "A word by itself is easy to guess.", \
           "Gives specific error for single-word passwords"

def test_empty_password():
    input_ = None
    password = ""

    try:
      zxcvbn(password, user_inputs=[input_])
    except IndexError as ie:
        assert False, "Empty password raised IndexError"

def test_chinese_language_support():
    # test Chinese translation
    password = "musculature"
    result = zxcvbn(password, lang='zh_Hans')
    
    assert result["feedback"]["warning"] == \
           "单个词语容易被猜中。", \
           "Returns Chinese translation for single-word passwords"

def test_french_language_support():
    # test French translation
    password = "musculature"
    result = zxcvbn(password, lang='fr_FR')
    
    assert result["feedback"]["warning"] == \
           "Un mot seul est facile à deviner.", \
           "Returns French translation for single-word passwords"

def test_language_fallback():
    # test fallback to English when translation not found
    password = "musculature"
    
    # For unsupported language
    result = zxcvbn(password, lang='es')  # Spanish not installed
    assert result["feedback"]["warning"] == \
           "A word by itself is easy to guess.", \
           "Falls back to English for unsupported languages"
           
    # For default case
    result = zxcvbn(password)  # No language specified
    assert result["feedback"]["warning"] == \
           "A word by itself is easy to guess.", \
           "Falls back to English when no language specified"
