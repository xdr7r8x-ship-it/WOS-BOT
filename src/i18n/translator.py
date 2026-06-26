import logging
from typing import Optional
from src.i18n.ar import ARABIC_TRANSLATIONS
from src.i18n.en import ENGLISH_TRANSLATIONS

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ["ar", "en"]
DEFAULT_LANGUAGE = "ar"

_translations = {
    "ar": ARABIC_TRANSLATIONS,
    "en": ENGLISH_TRANSLATIONS,
}

_missing_keys_cache = set()


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    if not key:
        return ""
    
    lang = validate_language(lang)
    
    translation = _translations.get(lang, {}).get(key)
    
    if translation is None:
        translation = _translations.get(DEFAULT_LANGUAGE, {}).get(key)
    
    if translation is None:
        if key not in _missing_keys_cache:
            _missing_keys_cache.add(key)
            logger.warning(f"Missing translation key: {key}")
        return key
    
    if kwargs:
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            logger.warning(f"Error formatting translation {key}: {e}")
            return translation
    
    return translation


def validate_language(lang: str) -> str:
    if not lang or not isinstance(lang, str):
        return DEFAULT_LANGUAGE
    
    lang = lang.strip().lower()
    
    if lang in SUPPORTED_LANGUAGES:
        return lang
    
    return DEFAULT_LANGUAGE


def get_supported_languages() -> list:
    return SUPPORTED_LANGUAGES.copy()


def get_all_keys() -> set:
    return set(ARABIC_TRANSLATIONS.keys())


def verify_key_coverage() -> dict:
    ar_keys = set(ARABIC_TRANSLATIONS.keys())
    en_keys = set(ENGLISH_TRANSLATIONS.keys())
    
    only_in_ar = ar_keys - en_keys
    only_in_en = en_keys - ar_keys
    
    return {
        "total_keys": len(ar_keys),
        "complete": len(only_in_ar) == 0 and len(only_in_en) == 0,
        "only_in_ar": list(only_in_ar),
        "only_in_en": list(only_in_en),
    }
