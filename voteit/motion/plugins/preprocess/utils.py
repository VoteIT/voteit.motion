from arche.portlets import get_portlet_manager
from pyramid.httpexceptions import HTTPNotFound


def get_portlet(request, portlet_uid):
    slot = 'agenda_item'
    manager = get_portlet_manager(request.meeting, request.registry)
    slot_portlets = manager.get(slot, {})
    portlet = slot_portlets.get(portlet_uid, None)
    if portlet is None:
        raise HTTPNotFound("The preprocess portlet wasn't found")
    return portlet
