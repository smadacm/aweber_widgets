from django.http import HttpResponse
from django.views import generic
from django.core.exceptions import ObjectDoesNotExist

from . import models


def render_response(error_number: int = 0, error_message: str = '', widgets: tuple[models.Widget] = None):
    """ The entire point of this function is to ensure uniform response. """

    resp_obj = models.Response(error_number=error_number, error_message=error_message, widgets=widgets)
    return HttpResponse(resp_obj.dumps())


# Create your views here.
class Widgets(generic.View):
    # list all widgets
    def get(self, request, *args, **kwargs):
        return render_response(widgets=models.Widget.objects.all())

    # create
    def put(self, request, *args, **kwargs):
        pass


class ExistingWidget(generic.View):
    # read
    def get(self, request, id, *args, **kwargs):
        try:
            possibles = (models.Widget.objects.get(pk=id),)
        except ObjectDoesNotExist:
            possibles = None
        return render_response(error_number=models.ERR_A_OK if possibles else models.ERR_MODEL_DOES_NOT_EXIST,
                               widgets=possibles)

    # update
    def patch(self, request, id, *args, **kwargs):
        pass

    # delete
    def delete(self, request, id, *args, **kwargs):
        pass
