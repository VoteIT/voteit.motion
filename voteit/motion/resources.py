from __future__ import unicode_literals

import string
from random import choice

from BTrees.OOBTree import OOBTree
from arche.api import Content
from arche.api import ContextACLMixin
from arche.api import LocalRolesMixin
from arche.utils import utcnow
from persistent.list import PersistentList
from zope.interface import implementer

from voteit.motion import _
from voteit.motion.intefaces import IMotionProcess
from voteit.motion.intefaces import IMotion
from voteit.motion.permissions import ADD_MOTION
from voteit.motion.permissions import ADD_MOTION_PROCESS


@implementer(IMotionProcess)
class MotionProcess(Content, ContextACLMixin, LocalRolesMixin):
    default_view = "view"
    nav_visible = True
    type_name = "MotionProcess"
    type_title = _("Motion process")
    add_permission = ADD_MOTION_PROCESS
    css_icon = "glyphicon glyphicon-inbox"
    body = ""


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
    _proposals = ()
    _creator = ()
    _endorsements = {}

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
        #Add new with timestamp
        for userid in set(value) - set(self._endorsements):
            self._endorsements[userid] = utcnow()
        #Remove no longer endorsing userids
        for userid in set(self._endorsements) - set(value):
            del self._endorsements[userid]

    @property
    def endorsements_info(self):
        return self._endorsements.items()

    def enable_sharing_token(self):
        self.sharing_token = "".join([choice(string.letters + string.digits) for x in range(15)])
        return self.sharing_token

    def remove_sharing_token(self):
        self.sharing_token = None


def includeme(config):
    config.add_content_factory(MotionProcess, addable_to=['Root', 'Folder'])
    config.add_content_factory(Motion, addable_to='MotionProcess')
