from django import template

register = template.Library()

@register.filter
def get_item(list_or_dict, key):
    if isinstance(list_or_dict, list):
        return list_or_dict[int(key)] if int(key) < len(list_or_dict) else ''
    elif isinstance(list_or_dict, dict):
        return list_or_dict.get(str(key), '')
    return ''

