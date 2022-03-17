import json
import datetime

from django.db import models

ERR_A_OK = 0
ERR_MODEL_DOES_NOT_EXIST = 1
ERR_INVALID_DATA = 2
ERR_MALFORMED_DATA = 3

possible_errors = {
    ERR_A_OK: 'Everything is fine.',
    ERR_MODEL_DOES_NOT_EXIST: 'The requested object does not exist.',
    ERR_INVALID_DATA: 'The required data was not valid.',
    ERR_MALFORMED_DATA: 'Unable to parse supplied data.',
}

NAME_MAX_LENGTH = 64


def json_render_field(field):
    if type(field) in (str, int): return field
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


class Response:
    """
    object to jsonify  for response to client
    reckon this should probably be in a view_models.py, but that seems like over-normalization
    """
    def __init__(self, error_number: int = 0, error_message: str = '', widgets: tuple[Widget] = None):
        self.error_number: int = error_number
        self.error_message: str = error_message
        self.widgets: tuple[Widget] = widgets

    def dumps(self):
        if not self.error_message:
            self.error_message = possible_errors.get(self.error_number, self.error_message)
        return json.dumps({
            'error_number': self.error_number,
            'error_message': self.error_message,
            'widgets': tuple(w.to_dict() for w in self.widgets)
        }, default=json_render_field)
