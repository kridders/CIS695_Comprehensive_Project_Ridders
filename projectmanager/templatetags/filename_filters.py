from django import template
import os

register = template.Library()

@register.filter
def basename_noext(value):
    """
    Gibt den Dateiname ohne Pfad und ohne Extension zurück
    """
    return os.path.splitext(os.path.basename(value))[0]
