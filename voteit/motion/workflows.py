from __future__ import unicode_literals

from arche.models.workflow import Workflow

from voteit.core.security import ROLE_ADMIN
from voteit.core.security import VIEW
from voteit.core.security import EDIT
from voteit.core.security import CHANGE_WORKFLOW_STATE
from voteit.motion import _

from voteit.motion.permissions import ADD_MOTION


_ADMIN_PERMS = (
    CHANGE_WORKFLOW_STATE,
    EDIT,
    VIEW,
    ADD_MOTION,
)


class MotionProcessWorkflow(Workflow):
    name = 'motion_process_workflow'
    title = _("Motion process workflow")
    states = {'private': _("Private"),
              'open': _("Public"),
              'closed': _("Closed")}
    transitions = {}
    initial_state = 'private'

    @classmethod
    def init_acl(cls, registry):
        for sname in cls.states:
            acl_entry = registry.acl.new_acl(cls.name + ':' + sname)
            acl_entry.add(ROLE_ADMIN, _ADMIN_PERMS)

        # acl_priv = registry.acl.new_acl('%s:private' % cls.name)
        # acl_priv.add(ROLE_ADMIN, _ADMIN_PERMS)
        # acl_open = registry.acl.new_acl('%s:open' % cls.name)
        # acl_open.add(ROLE_ADMIN, _ADMIN_PERMS)
        # acl_closed = registry.acl.new_acl('%s:closed' % cls.name)
        # acl_closed.add(ROLE_ADMIN, _ADMIN_PERMS)


MotionProcessWorkflow.add_transitions(
    from_states='*',
    to_states='private',
    permission=CHANGE_WORKFLOW_STATE,
    title=_("Make private"),
)


MotionProcessWorkflow.add_transitions(
    from_states='*',
    to_states='closed',
    permission=CHANGE_WORKFLOW_STATE,
    title=_("Close process"),
)


MotionProcessWorkflow.add_transitions(
    from_states='*',
    to_states='open',
    permission=CHANGE_WORKFLOW_STATE,
    title=_("Open process"),
)


class MotionWorkflow(Workflow):
    name = 'motion_workflow'
    title = _("Motion workflow")
    states = {'draft': _("Draft"),
              'review': _("Under review"),
              'published': _("Published"),
              'lacked_endorsement': _("Lacked endorsement"),
              'endorsed': _("Has endorsement")}
    transitions = {}
    initial_state = 'draft'

    @classmethod
    def init_acl(cls, registry):
        for sname in cls.states:
            acl_entry = registry.acl.new_acl(cls.name + ':' + sname)
            acl_entry.add(ROLE_ADMIN, _ADMIN_PERMS)
        #acl_priv = registry.acl.new_acl('%s:private' % cls.name)
        #acl_priv.add(ROLE_ADMIN, _ADMIN_PERMS)
        #acl_open = registry.acl.new_acl('%s:open' % cls.name)
        #acl_open.add(ROLE_ADMIN, _ADMIN_PERMS)
        #acl_closed = registry.acl.new_acl('%s:closed' % cls.name)
        #acl_closed.add(ROLE_ADMIN, _ADMIN_PERMS)


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='draft',
    permission=CHANGE_WORKFLOW_STATE,
    title=_("Set as draft"),
)

MotionWorkflow.add_transitions(
    from_states='*',
    to_states='review',
    permission=CHANGE_WORKFLOW_STATE,
    title=_("Set as under review"),
  #  title=_("Close process"),
)


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='published',
    permission=CHANGE_WORKFLOW_STATE,
    title=_("Publish"),
)


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='lacked_endorsement',
    permission=CHANGE_WORKFLOW_STATE,
    title=_("Lacked endorsement"),
)


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='endorsed',
    permission=CHANGE_WORKFLOW_STATE,
    title=_("Has enough endorsements"),
)


def includeme(config):
    config.add_workflow(MotionProcessWorkflow)
    config.add_workflow(MotionWorkflow)
    config.set_content_workflow('MotionProcess', 'motion_process_workflow')
    config.set_content_workflow('Motion', 'motion_workflow')
