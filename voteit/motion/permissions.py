from voteit.core import security

ADD_MOTION_PROCESS = "Add motion process"
ADD_MOTION = "Add motion"
ENDORSE_MOTION = "Endorse motion"
CHECK_EMAIL_AGAINST_HASHLIST = "Check email against hashlist"
ENABLE_MOTION_SHARING = "Enable motion sharing"
ASSIGN_HASHTAGS = "Assign hashtags"


EDITOR_PERMS = [
    security.CHANGE_WORKFLOW_STATE,
    security.EDIT,
    security.VIEW,
    security.DELETE,
    ADD_MOTION,
    ENABLE_MOTION_SHARING, #May be blocked
]


ADMIN_PERMS = [
    security.PERM_MANAGE_USERS,
    security.MANAGE_SERVER,
    ASSIGN_HASHTAGS,
]


ADMIN_PERMS.extend(EDITOR_PERMS)

