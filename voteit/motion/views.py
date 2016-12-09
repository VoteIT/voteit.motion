from arche.security import PERM_EDIT
from arche.views.base import BaseView
from arche.views.base import DefaultEditForm
from pyramid.view import view_config
from voteit.core.security import CHANGE_WORKFLOW_STATE
from voteit.core.security import EDIT
from voteit.core.security import VIEW
from webhelpers.html.converters import nl2br
from webhelpers.html.render import sanitize
from webhelpers.html.tools import auto_link

from voteit.motion.intefaces import IMotion
from voteit.motion.intefaces import IMotionProcess


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


@view_config(context=IMotion,
             name='view',
             permission=VIEW,
             renderer='voteit.motion:templates/motion.pt')
class MotionView(BaseView):

    def __call__(self):
        can_submit = self.context.wf_state == 'draft' and \
                     self.request.has_permission(CHANGE_WORKFLOW_STATE, self.context)
        return {'can_submit': can_submit,
                'can_edit': self.request.has_permission(PERM_EDIT, self.context)}

    def format_text(self, text):
        text = sanitize(text)
        text = auto_link(text)
        return nl2br(text)


def includeme(config):
    config.scan(__name__)
