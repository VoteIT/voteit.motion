from __future__ import unicode_literals

import string
from random import choice

from BTrees.OOBTree import OOBTree
from arche.api import Content
from arche.api import ContextACLMixin
from arche.api import LocalRolesMixin
from arche.security import ROLE_EVERYONE
from arche.security import ROLE_AUTHENTICATED
from arche.security import ROLE_OWNER
from arche.security import PERM_VIEW
from arche.utils import utcnow
from persistent.list import PersistentList
from pyramid.security import Allow
from pyramid.security import Deny
from voteit.core.security import ROLE_VIEWER
from zope.interface import implementer

from voteit.motion import _
from voteit.motion.intefaces import IMotionProcess
from voteit.motion.intefaces import IMotion
from voteit.motion.permissions import ADD_MOTION
from voteit.motion.permissions import ADD_MOTION_PROCESS
from voteit.motion.permissions import ENDORSE_MOTION
from voteit.motion.permissions import ENABLE_MOTION_SHARING


@implementer(IMotionProcess)
class MotionProcess(Content, ContextACLMixin, LocalRolesMixin):
    default_view = "view"
    nav_visible = False
    type_name = "MotionProcess"
    type_title = _("Motion process")
    add_permission = ADD_MOTION_PROCESS
    css_icon = "glyphicon glyphicon-inbox"
    body = ""
    allow_endorsements = False
    allow_sharing_link = False
    allow_any_authenticated = False
    motion_visibility = "hidden"
    _hashlist_uids = ()

    @property
    def hashlist_uids(self):
        return self._hashlist_uids

    @hashlist_uids.setter
    def hashlist_uids(self, value):
        self._hashlist_uids = tuple(value)


@implementer(IMotion)
class Motion(Content, ContextACLMixin, LocalRolesMixin):
    default_view = "view"
    search_visible = True
    nav_visible = False
    type_name = "Motion"
    type_title = _("Motion")
    add_permission = ADD_MOTION
    css_icon = "glyphicon glyphicon-list-alt"
    body = ""
    endorsements_text = ""
    sharing_token = None
    hashtag = ""
    _proposals = ()
    _creator = ()
    _endorsements = {}

    @property
    def __acl__(self):
        acl_list = super(Motion, self).__acl__
        motion_proc = self.__parent__
        if motion_proc:
            if motion_proc.allow_endorsements == False:
                acl_list.insert(0, (Deny, ROLE_EVERYONE, (ENDORSE_MOTION,)))
            if motion_proc.allow_sharing_link == True:
                acl_list.insert(0, (Allow, ROLE_OWNER, (ENABLE_MOTION_SHARING,)))
            wf = self.workflow
            state = ""
            if wf:
                state = wf.state in wf.states and wf.state or wf.initial_state
            if state and state != "draft":
                if motion_proc.motion_visibility == "authenticated":
                    acl_list.insert(0, (Allow, ROLE_AUTHENTICATED, (PERM_VIEW,)))
                if motion_proc.motion_visibility == "everyone":
                    acl_list.insert(0, (Allow, ROLE_EVERYONE, (PERM_VIEW,)))
        return acl_list

    @property
    def proposals(self):
        return tuple(self._proposals)

    @proposals.setter
    def proposals(self, value):
        if not isinstance(self._proposals, PersistentList):
            self._proposals = PersistentList()
        if tuple(value) != tuple(self._proposals):
            self._proposals[:] = []
            self._proposals.extend(value)

    @property
    def creator(self):
        return tuple(self._creator)

    @creator.setter
    def creator(self, value):
        if tuple(value) != self._creator:
            self._creator = tuple(value)

    @property
    def endorsements(self):
        return tuple(self._endorsements)

    @endorsements.setter
    def endorsements(self, value):
        if not isinstance(self._endorsements, OOBTree):
            self._endorsements = OOBTree()
        # Add new with timestamp
        for userid in set(value) - set(self._endorsements):
            self.local_roles.add(userid, ROLE_VIEWER)
            self._endorsements[userid] = utcnow()
        # Remove no longer endorsing userids
        for userid in set(self._endorsements) - set(value):
            del self._endorsements[userid]
            self.local_roles.remove(userid, ROLE_VIEWER)

    @property
    def endorsements_info(self):
        return self._endorsements.items()

    def enable_sharing_token(self):
        self.sharing_token = "".join(
            [choice(string.letters + string.digits) for x in range(15)]
        )
        return self.sharing_token

    def remove_sharing_token(self):
        self.sharing_token = None


def includeme(config):
    config.add_content_factory(MotionProcess, addable_to=["Root", "Folder"])
    config.add_content_factory(Motion, addable_to="MotionProcess")
    # Patch agenda items to remember where they came from
    from voteit.core.models.agenda_item import AgendaItem

    # old-style properties for this...
    # FIXME: will be changed in VoteIT
    def _get_motion_uid(self):
        return self.get_field_value("motion_uid", "")

    def _set_motion_uid(self, value):
        self.set_field_value("motion_uid", value)

    AgendaItem.motion_uid = property(_get_motion_uid, _set_motion_uid)
