from django import template
from encounters.models import AnnouncementSeen

register = template.Library()

# Change this name when you write a new announcement, so everyone sees it once.
# The message itself is in templates/encounters/announcement.html
CURRENT_ANNOUNCEMENT = '2026-10-companion-and-handlers'


@register.inclusion_tag('encounters/announcement.html', takes_context=True)
def show_announcement(context):
    user = context['request'].user
    if not user.is_authenticated:
        return {'show': False}
    # created is True only the first time, so the pop-up shows once per user
    seen, created = AnnouncementSeen.objects.get_or_create(user=user, announcement=CURRENT_ANNOUNCEMENT)
    return {'show': created}
