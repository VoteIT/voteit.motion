from arche.security import PERM_EDIT
from arche.views.base import BaseView
from arche.views.base import DefaultEditForm
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config, view_defaults
from voteit.core.security import CHANGE_WORKFLOW_STATE
from voteit.core.security import EDIT
from voteit.core.security import VIEW
from voteit.motion.permissions import ENABLE_MOTION_SHARING
from webhelpers.html.converters import nl2br
from webhelpers.html.render import sanitize
from webhelpers.html.tools import auto_link

from voteit.motion.intefaces import IMotion
from voteit.motion.intefaces import IMotionProcess
from voteit.motion import _


@view_config(context=IMotionProcess,
             name='view',
             permission=VIEW,
             renderer='voteit.motion:templates/motion_process.pt')
class MotionProcessView(BaseView):

    def __call__(self):
        return {}

    def get_motions(self):
        for obj in self.context.values():
            if IMotion.providedBy(obj) and self.request.has_permission(VIEW, obj):
                yield obj


@view_config(context=IMotion,
             name='edit_endorsements',
             permission=EDIT,
             renderer='arche:templates/form.pt')
class EditEndorsementsForm(DefaultEditForm):
    schema_name = 'endorsements'


@view_defaults(
    context=IMotion,
    renderer='voteit.motion:templates/motion.pt')
class MotionView(BaseView):

    @view_config(name='view', permission=VIEW)
    def main_view(self):
        can_submit = self.context.wf_state == 'draft' and \
                     self.request.has_permission(CHANGE_WORKFLOW_STATE, self.context)
        return {'can_submit': can_submit,
                'can_edit': self.request.has_permission(PERM_EDIT, self.context)}

    @view_config(name='_ts', permission=NO_PERMISSION_REQUIRED)
    def token_view(self):
        if not self.context.sharing_token:
            raise HTTPNotFound()
        if self.request.subpath and self.request.subpath[0] == self.context.sharing_token:
            return self.main_view()
        raise HTTPNotFound()

    def format_text(self, text):
        text = sanitize(text)
        text = auto_link(text)
        return nl2br(text)

    @view_config(name="toggle_sharing", permission=ENABLE_MOTION_SHARING)
    def toggle_sharing(self):
        state = self.request.GET.get('s', None)
        if state == 'on':
            self.context.enable_sharing_token()
            self.flash_messages.add(_("sharing_switched_on",
                                      default="Sharing enalbed - use the link below."),
                                    type='success')
        if state == 'off':
            self.context.remove_sharing_token()
            self.flash_messages.add(_("sharing_switched_off",
                                      default="Sharing switched off - motion not accessible unless you're logged in."),
                                    type='warning')
        return HTTPFound(location=self.request.resource_url(self.context))


def includeme(config):
    config.scan(__name__)
