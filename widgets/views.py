import json
import typing

from django.http import HttpResponse, HttpRequest
from django.views import generic
from django.core.exceptions import ObjectDoesNotExist

from . import models


# errors
# format is tuple(error_number, error_message, http_status) where error_number is just an arbitrary int
ERR_A_OK = (0, 'Everything is fine.', 200)
ERR_MODEL_DOES_NOT_EXIST = (1, 'The requested object does not exist.', 404)
ERR_INVALID_DATA = (2, 'The required data was not valid.', 400)
ERR_MALFORMED_DATA = (3, 'Unable to parse supplied data', 400)


def render_response(error: tuple[int, str, int] = ERR_A_OK, error_message: str = '',
                    widgets: tuple[models.Widget] = None) -> HttpResponse:
    """ The entire point of this function is to ensure uniform response. """

    error_message = error_message or error[1]

    resp_d = {
        'error_number': error[0],
        'error_message': error_message,
        'widgets': tuple(w.to_dict() for w in widgets) if widgets else (),
    }

    return HttpResponse(json.dumps(resp_d, default=models.json_render_field), status=error[2])


def _get_widget_or_none(widget_id: int) -> models.Widget:
    widget = None
    try:
        widget = models.Widget.objects.get(pk=widget_id)
    except ObjectDoesNotExist:
        pass  # widget will be None

    return widget


def create_or_update_widget(raw_body: str, widget_id: typing.Optional[int] = None) -> HttpResponse:
    """
    take the raw request body, and possibly a widget id, get or create the widget,
    apply the user's input, save it, and return a response object that can be returned by a view
    """
    error = ERR_A_OK
    error_message = ''

    # these 2 slightly increase memory footprint, but if there's no default, pycharm fusses
    cleaned_input = {}
    parsed_body = {}

    # get or create widget based on presence of widget_id
    if widget_id is not None:
        widget = _get_widget_or_none(widget_id)
        if not widget:
            error = ERR_MODEL_DOES_NOT_EXIST
    else:
        widget = models.Widget()

    # parse request body to dict
    if not error:
        try:
            parsed_body = json.loads(raw_body)
        except json.JSONDecodeError as err:
            error = ERR_MALFORMED_DATA

    # check data is clean
    if not error:
        err_msgs = []

        # if this is a new object, require all fields
        if widget_id is None:
            for k in ('name', 'parts_count'):
                if k not in parsed_body:
                    err_msgs.append(f'Missing "{k}" parameter.')

        # check that parts_count is an int
        if type(parsed_body.get('parts_count', 0)) != int:
            err_msgs.append('"parts_count" parameter must be an int.')
        # check that parts_count is an int
        if 'name' in parsed_body and type(parsed_body['name']) != str:
            err_msgs.append('"name" parameter must be a str.')
        # check name max length
        elif 'name' in parsed_body and len(parsed_body['name']) > models.NAME_MAX_LENGTH:
            err_msgs.append(f'"name" parameter is longer than maximum {models.NAME_MAX_LENGTH} characters.')

        # any error message means failure
        if err_msgs:
            error = ERR_INVALID_DATA
            error_message = ' '.join(err_msgs)

    # if we get this far, the input is valid, so update the widget and save
    if not error:
        if 'name' in cleaned_input:
            widget.name = cleaned_input['name']
        if 'parts_count' in cleaned_input:
            widget.name = cleaned_input['parts_count']

        widget.save()

    # return the error or created/updated widget
    return render_response(error=error, error_message=error_message or None, widgets=(widget,))


# The actual views
class Widgets(generic.View):
    # list all widgets
    def get(self, request: HttpRequest, *args: [any], **kwargs: dict) -> HttpResponse:
        return render_response(widgets=models.Widget.objects.all())

    # create
    def put(self, request: HttpRequest, *args: [any], **kwargs: dict) -> HttpResponse:
        return create_or_update_widget(raw_body=request.body)


class ExistingWidget(generic.View):
    # read
    def get(self, request: HttpRequest, widget_id: int, *args: [any], **kwargs: dict) -> HttpResponse:
        widget = _get_widget_or_none(widget_id)
        return render_response(error=ERR_A_OK if widget else ERR_MODEL_DOES_NOT_EXIST, widgets=(widget,))

    # update
    def patch(self, request: HttpRequest, widget_id: int, *args: [any], **kwargs: dict) -> HttpResponse:
        return create_or_update_widget(raw_body=request.body, widget_id=widget_id)

    # delete
    def delete(self, request: HttpRequest, widget_id: int, *args: [any], **kwargs: dict) -> HttpResponse:
        error = ERR_A_OK
        widget = _get_widget_or_none(widget_id)
        if not widget:
            error = ERR_MODEL_DOES_NOT_EXIST
        else:
            widget.delete()

        return render_response(error)
