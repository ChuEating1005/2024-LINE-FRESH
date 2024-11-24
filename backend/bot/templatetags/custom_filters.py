from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    自定義 template filter 用於獲取字典值
    用法: {{ my_dict|get_item:key }}
    """
    return dictionary.get(key)