from arche.views.base import BaseView, DefaultEditForm
from pyramid.view import view_config
from voteit.core.security import VIEW, EDIT
from voteit.motion.intefaces import IMotionProcess, IMotion


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


def includeme(config):
    config.scan(__name__)
