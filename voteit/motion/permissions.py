from voteit.core import security


ADD_MOTION_PROCESS = "Add motion process"
ADD_MOTION = "Add motion"


EDITOR_PERMS = [
    security.CHANGE_WORKFLOW_STATE,
    security.EDIT,
    security.VIEW,
    ADD_MOTION,
]


ADMIN_PERMS = [
    security.PERM_MANAGE_USERS
]
ADMIN_PERMS.extend(EDITOR_PERMS)

