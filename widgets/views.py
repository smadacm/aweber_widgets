import json
import typing

from django.http import HttpResponse, HttpRequest
from django.views import generic
from django.core.exceptions import ObjectDoesNotExist

from . import models


# TODO: all of this needs to be gone through for readability
# TODO: move models.Response under render_response(), add HTTP statuses

def render_response(error_number: int = 0, error_message: str = '', widgets: tuple[models.Widget] = None):
    """ The entire point of this function is to ensure uniform response. """

    resp_obj = models.Response(error_number=error_number, error_message=error_message, widgets=widgets)
    return HttpResponse(resp_obj.dumps())


def validate_input(body: str, all_required: bool = False) -> tuple[dict, int, str]:
    """ Clean input from the user """
    error_number = 0
    error_message = ''
    loaded = None

    try:
        loaded = json.loads(body)
    except json.JSONDecodeError as err:
        error_number = models.ERR_MALFORMED_DATA
    else:
        err_msgs = []

        if all_required:
            for k in ('name', 'parts_count'):
                if k not in loaded:
                    err_msgs.append(f'Missing "{k}" parameter.')

        if len(loaded.get('name', '')) > models.NAME_MAX_LENGTH:
            err_msgs.append(f'"name" parameter is longer than maximum {models.NAME_MAX_LENGTH} characters.')
        if type(loaded.get('parts_count', 0)) != int:
            err_msgs.append('"parts_count" parameter must be an int.')

        if err_msgs:
            error_number = models.ERR_INVALID_DATA
            error_message = ' '.join(err_msgs)

    return loaded, error_number, error_message


def get_widget_or_none(widget_id: int) -> typing.Optional[models.Widget]:
    """ mimics dict.get(), but without a modifiable default """
    possible_widget = None
    try:
        possible_widget = models.Widget.objects.get(pk=widget_id)
    except ObjectDoesNotExist:
        pass  # will fall back to possible_widgets = None above
    return possible_widget


def create_or_update_widget(raw_body: str, widget_id: typing.Optional[int] = None):
    """
    take the raw request body, and possibly a widget id, get or create the widget,
    apply the user's input, save it, and return a response object that can be returned by a view
    """
    error_number = 0
    error_message = ''
    cleaned_input = {} # slightly increases memory footprint, but if there's no default, pycharm fusses

    if widget_id:
        widget = get_widget_or_none(widget_id)
        if not widget:
            error_number = models.ERR_MODEL_DOES_NOT_EXIST
    else:
        widget = models.Widget()

    if not error_number:
        # ensure we have all info needed to create a Widget
        cleaned_input, error_number, error_message = validate_input(raw_body, widget_id is None)

    if not error_number:
        if 'name' in cleaned_input:
            widget.name = cleaned_input['name']
        if 'parts_count' in cleaned_input:
            widget.name = cleaned_input['parts_count']

        widget.save()

    return render_response(error_number=error_number, error_message=error_message or None, widgets=(widget,))


# Create your views here.
class Widgets(generic.View):
    # list all widgets
    def get(self, request: HttpRequest, *args: [any], **kwargs: dict) -> HttpResponse:
        return render_response(widgets=models.Widget.objects.all())

    # create
    def put(self, request: HttpRequest, *args: [any], **kwargs: dict) -> HttpResponse:
        body = request.body
        return create_or_update_widget(raw_body=body)


class ExistingWidget(generic.View):
    # read
    def get(self, request: HttpRequest, widget_id: int, *args: [any], **kwargs: dict) -> HttpResponse:
        possible_widget = get_widget_or_none(widget_id)
        return render_response(error_number=models.ERR_A_OK if possible_widget else models.ERR_MODEL_DOES_NOT_EXIST,
                               widgets=possible_widget)

    # update
    def patch(self, request: HttpRequest, widget_id: int, *args: [any], **kwargs: dict) -> HttpResponse:
        body = request.body
        return create_or_update_widget(raw_body=body, widget_id=widget_id)

    # delete
    def delete(self, request: HttpRequest, widget_id: int, *args: [any], **kwargs: dict) -> HttpResponse:
        error_number = models.ERR_A_OK
        widget = get_widget_or_none(widget_id)
        if not widget:
            error_number = models.ERR_MODEL_DOES_NOT_EXIST
        else:
            widget.delete()

        return render_response(error_number)
