from __future__ import unicode_literals

from arche.models.workflow import Workflow
from arche.security import ROLE_AUTHENTICATED
from arche.security import ROLE_EDITOR
from arche.security import ROLE_EVERYONE
from voteit.core import security

try:
    from arche_comments.security import ADD_COMMENT
    from arche_comments.security import DELETE_COMMENT
    from arche_comments.security import EDIT_COMMENT
    from arche_comments.security import ENABLE_COMMENTS

    has_comments = True
except ImportError:
    has_comments = False

from voteit.motion import _
from voteit.motion.permissions import ADD_MOTION
from voteit.motion.permissions import CHECK_EMAIL_AGAINST_HASHLIST
from voteit.motion.permissions import ADMIN_PERMS
from voteit.motion.permissions import ENDORSE_MOTION
from voteit.motion.permissions import EDITOR_PERMS
from voteit.motion.security import ROLE_MOTION_PROCESS_PARTICIPANT


class MotionProcessWorkflow(Workflow):
    name = "motion_process_workflow"
    title = _("Motion process workflow")
    states = {"private": _("Private"), "open": _("Open"), "closed": _("Closed")}
    transitions = {}
    initial_state = "private"

    @classmethod
    def init_acl(cls, registry):
        for sname in cls.states:
            acl_entry = registry.acl.new_acl(cls.name + ":" + sname)
            acl_entry.add(security.ROLE_ADMIN, ADMIN_PERMS)
            acl_entry.add(ROLE_EDITOR, EDITOR_PERMS)
            if sname != "private":
                acl_entry.add(ROLE_EVERYONE, [security.VIEW])
            if sname == "open":
                acl_entry.add(ROLE_MOTION_PROCESS_PARTICIPANT, [ADD_MOTION])
                acl_entry.add(ROLE_AUTHENTICATED, [CHECK_EMAIL_AGAINST_HASHLIST])


MotionProcessWorkflow.add_transitions(
    from_states="*",
    to_states="private",
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Make private"),
)


MotionProcessWorkflow.add_transitions(
    from_states="*",
    to_states="closed",
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Close process"),
)


MotionProcessWorkflow.add_transitions(
    from_states="*",
    to_states="open",
    permission=security.CHANGE_WORKFLOW_STATE,
    title=_("Open process"),
)


class MotionWorkflow(Workflow):
    name = "motion_workflow"
    title = _("Motion workflow")
    states = {
        "draft": _("Draft"),
        "review": _("Under review"),
        "awaiting_endorsement": _("Awaiting endorsements"),
        "lacked_endorsement": _("Lacked enough endorsements"),
        "endorsed": _("Has enough endorsements"),
    }
    transitions = {}
    initial_state = "draft"

    @classmethod
    def init_acl(cls, registry):
        for sname in cls.states:
            acl_entry = registry.acl.new_acl(cls.name + ":" + sname)
            acl_entry.add(security.ROLE_ADMIN, ADMIN_PERMS)
            acl_entry.add(ROLE_EDITOR, EDITOR_PERMS)
            acl_entry.add(security.ROLE_OWNER, [security.VIEW])
            acl_entry.add(security.ROLE_VIEWER, [security.VIEW])
            if sname != "lacked_endorsement":
                acl_entry.add(ROLE_MOTION_PROCESS_PARTICIPANT, [ENDORSE_MOTION])
            if has_comments:
                acl_entry.add(ROLE_MOTION_PROCESS_PARTICIPANT, [ADD_COMMENT])
                acl_entry.add(
                    security.ROLE_OWNER,
                    [ENABLE_COMMENTS, ADD_COMMENT, DELETE_COMMENT, EDIT_COMMENT],
                )
                acl_entry.add(
                    security.ROLE_ADMIN,
                    [ENABLE_COMMENTS, ADD_COMMENT, DELETE_COMMENT, EDIT_COMMENT],
                )
                acl_entry.add(ROLE_EDITOR, [ENABLE_COMMENTS, ADD_COMMENT])
        registry.acl[cls.name + ":draft"].add(
            security.ROLE_OWNER,
            [security.EDIT, security.CHANGE_WORKFLOW_STATE, security.DELETE],
        )


MotionWorkflow.add_transitions(
    from_states="draft",
    to_states=["review", "awaiting_endorsement"],
    permission=security.CHANGE_WORKFLOW_STATE,
)


MotionWorkflow.add_transitions(
    from_states="review", to_states="*", permission=security.CHANGE_WORKFLOW_STATE
)


MotionWorkflow.add_transitions(
    from_states="awaiting_endorsement",
    to_states="*",
    permission=security.CHANGE_WORKFLOW_STATE,
)


MotionWorkflow.add_transitions(
    from_states="lacked_endorsement",
    to_states="awaiting_endorsement",
    permission=security.CHANGE_WORKFLOW_STATE,
)


MotionWorkflow.add_transitions(
    from_states="endorsed",
    to_states="awaiting_endorsement",
    permission=security.CHANGE_WORKFLOW_STATE,
)


def includeme(config):
    config.add_workflow(MotionProcessWorkflow)
    config.add_workflow(MotionWorkflow)
    config.set_content_workflow("MotionProcess", "motion_process_workflow")
    config.set_content_workflow("Motion", "motion_workflow")
