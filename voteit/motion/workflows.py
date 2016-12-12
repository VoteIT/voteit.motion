from __future__ import unicode_literals

from arche.models.workflow import Workflow
from arche.security import ROLE_AUTHENTICATED
from arche.security import ROLE_EDITOR
from voteit.core import security

from voteit.motion import _
from voteit.motion.permissions import ADD_MOTION
from voteit.motion.permissions import CHECK_EMAIL_AGAINST_HASHLIST
from voteit.motion.permissions import ENABLE_MOTION_SHARING
from voteit.motion.permissions import ADMIN_PERMS
from voteit.motion.permissions import ENDORSE_MOTION
from voteit.motion.permissions import EDITOR_PERMS
from voteit.motion.security import ROLE_MOTION_PROCESS_PARTICIPANT


class MotionProcessWorkflow(Workflow):
    name = 'motion_process_workflow'
    title = _("Motion process workflow")
    states = {'private': _("Private"),
              'open': _("Open"),
              'closed': _("Closed")}
    transitions = {}
    initial_state = 'private'

    @classmethod
    def init_acl(cls, registry):
        for sname in cls.states:
            acl_entry = registry.acl.new_acl(cls.name + ':' + sname)
            acl_entry.add(security.ROLE_ADMIN, ADMIN_PERMS)
            acl_entry.add(ROLE_EDITOR, EDITOR_PERMS)
            if sname != 'private':
                acl_entry.add(ROLE_AUTHENTICATED, [security.VIEW])
            if sname == 'open':
                acl_entry.add(ROLE_MOTION_PROCESS_PARTICIPANT, [ADD_MOTION])
                acl_entry.add(ROLE_AUTHENTICATED, [CHECK_EMAIL_AGAINST_HASHLIST])


MotionProcessWorkflow.add_transitions(
    from_states='*',
    to_states='private',
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Make private"),
)


MotionProcessWorkflow.add_transitions(
    from_states='*',
    to_states='closed',
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Close process"),
)


MotionProcessWorkflow.add_transitions(
    from_states='*',
    to_states='open',
    permission=security.CHANGE_WORKFLOW_STATE,
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
            acl_entry.add(security.ROLE_ADMIN, ADMIN_PERMS)
            acl_entry.add(ROLE_EDITOR, EDITOR_PERMS)
            acl_entry.add(security.ROLE_OWNER, [security.VIEW, ENABLE_MOTION_SHARING])
            if sname != 'lacked_endorsement':
                acl_entry.add(ROLE_MOTION_PROCESS_PARTICIPANT, [ENDORSE_MOTION])
        registry.acl[cls.name+':draft'].add(security.ROLE_OWNER,
                                            [security.EDIT, security.CHANGE_WORKFLOW_STATE])


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='draft',
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Set as draft"),
)


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='review',
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Set as under review"),
)


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='published',
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Publish"),
)


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='lacked_endorsement',
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Lacked endorsement"),
)


MotionWorkflow.add_transitions(
    from_states='*',
    to_states='endorsed',
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Has enough endorsements"),
)


def includeme(config):
    config.add_workflow(MotionProcessWorkflow)
    config.add_workflow(MotionWorkflow)
    config.set_content_workflow('MotionProcess', 'motion_process_workflow')
    config.set_content_workflow('Motion', 'motion_workflow')
