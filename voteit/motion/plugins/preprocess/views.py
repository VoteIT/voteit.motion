from arche.views.base import BaseForm, BaseView
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
from six import string_types
from voteit.core.models.interfaces import IAgendaItem
from voteit.core.security import VIEW

from voteit.motion import _
from voteit.motion.plugins.preprocess.interfaces import IPreprocessUserTags
from voteit.motion.plugins.preprocess.utils import get_portlet


@view_config(context = IAgendaItem,
             name='_preprocess_form',
             renderer='arche:templates/form.pt',
             permission=VIEW)
class PreprocessForm(BaseForm):
    schema_name = "preprocess_tags"
    type_name = "AgendaItem"
    formid = 'preprocess_form'
    use_ajax = True
    ajax_options = """
            {success:
              function () {
                //alert('all done');
              },
            error:
              function (jqxhr) {
                arche.flash_error(jqxhr);
              }
            }
        """

    @reify
    def portlet(self):
        portlet_uid = self.request.GET.get('portlet', '')
        return get_portlet(self.request, portlet_uid)

    @reify
    def storage(self):
        return IPreprocessUserTags(self.context)

    @reify
    def can_add(self):
        return self.portlet.portlet_adapter.is_open(self.context, self.request)

    @property
    def buttons(self):
        buttons = []
        if self.can_add:
            buttons.append(self.button_save)
        if self.can_add and self.appstruct().get('tags', None):
            buttons.append(self.button_delete)
        buttons.append(self.button_close)
        return buttons

    def appstruct(self):
        return {
            'tags': self.storage.get(self.request.authenticated_userid, None)
        }

    def get_bind_data(self):
        return {'context': self.context, 'request': self.request, 'view': self, 'portlet': self.portlet}

    def save_success(self, appstruct):
        if not self.can_add:
            raise HTTPForbidden("You can't add tags here")
        self.storage[self.request.authenticated_userid] = appstruct['tags']
        msg = _("Saved")
        self.flash_messages.add(msg, type="success")
        return self._remove_modal_response()

    def delete_success(self, appstruct):
        self.storage.pop(self.request.authenticated_userid, None)
        msg = _("Settings removed")
        self.flash_messages.add(msg, type="info")
        return self._remove_modal_response()
    delete_failure = delete_success

    def close_success(self, *args):
        return self._remove_modal_response()
    close_failure = close_success

    def _remove_modal_response(self, *args):
        return Response(render("arche:templates/deform/destroy_modal.pt", {}, request = self.request))


@view_config(context = IAgendaItem,
             name='_preprocess_results',
             renderer='voteit.motion.plugins.preprocess:templates/results.pt',
             permission=VIEW)
class PreprocessResultsView(BaseView):

    @reify
    def portlet(self):
        portlet_uid = self.request.GET.get('portlet', '')
        return get_portlet(self.request, portlet_uid)

    def __call__(self):
        tags = IPreprocessUserTags(self.context)
        results = {}
        for row in tags.values():
            if isinstance(row, string_types):
                results.setdefault(row, 0)
                results[row] += 1
            else:
                for k in row:
                    results.setdefault(k, 0)
                    results[k] += 1
        tags = dict([(x['name'], x['title']) for x in self.portlet.settings.get('tags_selectable', ())])
        return {'tags': tags, 'results': results}


def includeme(config):
    config.scan(__name__)
