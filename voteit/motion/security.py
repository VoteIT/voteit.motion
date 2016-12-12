from arche.models.roles import Role

from voteit.motion import _
from voteit.motion.intefaces import IMotionProcess


ROLE_MOTION_PROCESS_PARTICIPANT = Role(
    'role:MotionProcParticipant',
    title = _("Participate motion proc."),
    inheritable = True,
    assignable = True,
    required = IMotionProcess)


def includeme(config):
    config.register_roles(
        ROLE_MOTION_PROCESS_PARTICIPANT,
    )
