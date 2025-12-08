from django.core.cache import cache
from django.utils.translation import get_language
from deep_translator import GoogleTranslator
from django import template

register = template.Library()

@register.simple_tag
def translate(text, source=None, target=None):
    try:
        if not target:
            target = 'en'
        if not source:
            source = get_language()
        
        # Create a unique cache key based on the source, target, and text
        cache_key = f"translation_{source}_{target}_{text}"
        cached_translation = cache.get(cache_key)
        
        if cached_translation:
            return cached_translation

        # Perform translation and cache the result
        translator = GoogleTranslator(source='auto', target=target) 
        translated_text = translator.translate(text)
        cache.set(cache_key, translated_text, timeout=3600)  # Cache for 1 hour
        return translated_text
    except Exception as e:
        return f"Error: {str(e)}"
