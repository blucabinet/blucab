from django import template

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()
