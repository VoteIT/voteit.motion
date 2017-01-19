from arche.utils import generate_slug
from pyramid.traversal import resource_path
from repoze.catalog.query import Eq
from voteit.core.security import ROLE_VIEWER


def _get_motions(request, context):
    query = Eq('type_name', 'Motion') & \
            Eq('wf_state', 'endorsed') & \
            Eq('path', resource_path(context))
    docids = request.root.catalog.query(query, sort_index='created')[1]
    return request.resolve_docids(docids, perm=None)


def export_into_meeting(request, motion_process, meeting, as_userid='', view_perm=True):
    results = {'prop': 0, 'ai': 0}
    creators = set()
    for motion in _get_motions(request, motion_process):
        creators.update(set(motion.creator))
        results['ai'] += 1
        ai = request.content_factories['AgendaItem'](
            title=motion.title,
            description=motion.description,
            body=motion.body,
        )
        name = generate_slug(meeting, ai.title)
        meeting[name] = ai
        for prop_text in motion.proposals:
            results['prop'] += 1
            if as_userid:
                creator = (as_userid,)
            else:
                creator = tuple(motion.creator)
            proposal = request.content_factories['Proposal'](
                text=prop_text,
                creator=creator,
            )
            name = generate_slug(ai, proposal.text)
            ai[name] = proposal
    for userid in creators:
        meeting.local_roles.add(userid, ROLE_VIEWER)
    return results
