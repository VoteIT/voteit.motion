from datetime import timedelta

from arche.utils import generate_slug
from arche.utils import utcnow
from pyramid.traversal import resource_path
from repoze.catalog.query import Any
from repoze.catalog.query import Eq
from voteit.core.helpers import tags2links
from voteit.core.security import ROLE_OWNER
from voteit.core.security import ROLE_VIEWER
from webhelpers.html.converters import nl2br
from webhelpers.html.tools import auto_link


def _get_motions(request, context, states):
    query = Eq('type_name', 'Motion') & \
            Any('wf_state', states) & \
            Eq('path', resource_path(context))
    docids = request.root.catalog.query(query, sort_index='created')[1]
    return request.resolve_docids(docids, perm=None)


def _transform_text(text):
    text = auto_link(text)
    text = nl2br(text)
    return tags2links(unicode(text))


def export_into_meeting(request, motion_process, meeting,
                        as_userid='',
                        view_perm=True,
                        clear_ownership=False,
                        states=['endorsed']):
    results = {'prop': 0, 'ai': 0}
    creators = set()
    for motion in _get_motions(request, motion_process, states):
        creators.update(set(motion.creator))
        results['ai'] += 1
        ai = request.content_factories['AgendaItem'](
            title=motion.title,
            description=motion.description,
            body=_transform_text(motion.body),
            hashtag=motion.hashtag,
            motion_uid=motion.uid,
        )
        name = generate_slug(meeting, ai.title)
        meeting[name] = ai
        now = utcnow()
        offset = 0
        for prop_text in motion.proposals:
            results['prop'] += 1
            if as_userid:
                creator = (as_userid,)
            else:
                creator = tuple(motion.creator)
            created = now + timedelta(seconds=offset)
            offset += 2
            proposal = request.content_factories['Proposal'](
                text=prop_text,
                creator=creator,
                created=created,
            )
            name = generate_slug(ai, proposal.text)
            ai[name] = proposal
            # There might be several subscribers that check for
            # ownership when an object is added to the resource tree.
            # Hence do this check afterwards.
            if clear_ownership:
                users_to_clear = set(proposal.local_roles.get_any_local_with(ROLE_OWNER))
                for userid in users_to_clear:
                    proposal.local_roles.remove(userid, ROLE_OWNER, event=False)
                if users_to_clear:
                    proposal.local_roles.send_event()
    if view_perm:
        for userid in creators:
            meeting.local_roles.add(userid, ROLE_VIEWER)
    return results
