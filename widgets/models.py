import datetime
import typing

from django.db import models

NAME_MAX_LENGTH = 64


def json_render_field(field: any) -> typing.Union[str, int]:
    if type(field) in (str, int):
        return field
    if type(field) == datetime.datetime:
        return field.isoformat()


class Widget(models.Model):
    """
    the entire purpose of this application is to track these do-dads
    id/pk is implied in django
    """
    name = models.CharField('Name', max_length=NAME_MAX_LENGTH, null=False, blank=False)
    parts_count = models.IntegerField('Number of parts', default=0, null=False, blank=False)

    created_at = models.DateTimeField('Created date/time', auto_now_add=True)
    updated_at = models.DateTimeField('Updated date/time', auto_now=True)

    def to_dict(self) -> dict:
        return {field.name: getattr(self, field.name) for field in Widget._meta.get_fields()}
