from __future__ import unicode_literals

import colander
import deform
from arche.widgets import deferred_autocompleting_userid_widget
from arche.widgets import ReferenceWidget
from voteit.core.security import MODERATE_MEETING

from voteit.motion import _


class MotionProcessSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        title=_("Title"),
    )
    description = colander.SchemaNode(
        colander.String(),
        title=_("Description"),
        missing="",
        description=_("schema_description",
                      default="Short description, visible as lead-in and on searches."),
    )
    body = colander.SchemaNode(
        colander.String(),
        title=_("Text body"),
        missing="",
        description=_("schema_body_description",
                      default="This is the description text for participants in the motion process. "
                              "It's always a good idea to include some basic instructions "
                              "and important dates as when the process opens and closes."),
        widget=deform.widget.RichTextWidget(),
    )
    allow_endorsements = colander.SchemaNode(
        colander.Bool(),
        title=_("Allow endorsements"),
    )
    allow_sharing_link = colander.SchemaNode(
        colander.Bool(),
        title=_("Allow users to create sharing link"),
        description=_("allow_sharing_link_schema_description",
                      default="If the motions are private, "
                              "allow users to create sharing links to "
                              "publish their motions to anyone.")
    )
    motion_visibility = colander.SchemaNode(
        colander.String(),
        title=_("Motion visibility"),
        widget=deform.widget.SelectWidget(
            values=(
                ('', _("<Select>")),
                ('hidden', _("All hidden (unless sharing links are used)")),
                ('authenticated', _("Logged in can read all non-drafts")),
                ('everyone', _("Visible to everyone")),
            )
        )
    )
    hashlist_uids = colander.SchemaNode(
        colander.Sequence(),
        colander.SchemaNode(
            colander.String(),
            name='not_used', #but required...
            title=_("Hashlists"),
            widget=ReferenceWidget(query_params={'type_name': 'HashList'}, multiple=False)
        ),
        title=_("hashlist_uids_schema_title",
                default="Users in this hashlist may gain permission to participate"),
        description=_("hashlist_uids_schema_description",
                      default="Requires package arche_hashlist to work. Users will need to "
                      "have their email address validated + pass a check against the hashlist.")
    )


class MotionSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        title=_("Title"),
    )
    description = colander.SchemaNode(
        colander.String(),
        title=_("Short description"),
        missing="",
        description=_("schema_description",
                      default="Short description, visible as lead-in and on searches."),
    )
    body = colander.SchemaNode(
        colander.String(),
        title=_("Text body"),
        missing="",
        description=_("Your motion text, excluding proposals"),
        widget=deform.widget.TextAreaWidget(rows=10),
    )
    proposals = colander.SchemaNode(
        colander.Sequence(),
        colander.SchemaNode(
            colander.String(),
            name='not_used',
            title=_("Proposal"),
            widget=deform.widget.TextAreaWidget(rows=3),
        ),
        title=_("Proposals - add at least one"),
        description=_("motion_proposals_schema_description",
                      default="Proposals must be written in a way so it's possible to approve or deny each one. "
                              "Don't give any background information or similar here."),
        widget=deform.widget.SequenceWidget(orderable=True),
        default=[''],
        validator=colander.Length(min=1,)
    )


class EditEndorsementsSchema(colander.Schema):
    endorsements = colander.SchemaNode(
        colander.Sequence(),
        colander.SchemaNode(
            colander.String(),
            name='foo',
            title=_("UserID"),
            widget=deferred_autocompleting_userid_widget,
        )
    )
    endorsements_text = colander.SchemaNode(
        colander.String(),
        title=_("Other endorsements"),
        description=_("written_endorsements_description",
                      default="From people who doesn't have an account here or perhaps from other groups."),
        missing="",
        widget=deform.widget.RichTextWidget(height=200),
    )


def _get_meetings(request):
    docids = request.root.catalog.query("type_name == 'Meeting'", sort_index='sortable_title')[1]
    values = []
    for meeting in request.resolve_docids(docids):
        if request.has_permission(MODERATE_MEETING, meeting):
            values.append(meeting)
    return values


@colander.deferred
def meetings_select_widget(node, kw):
    request = kw['request']
    meetings = _get_meetings(request)
    values = [('', _("<Select>"))]
    for meeting in meetings:
        values.append((meeting.__name__, "%s (%s)" % (meeting.title, meeting.__name__)))
    return deform.widget.SelectWidget(values=values)


@colander.deferred
def meetings_validator(node, kw):
    request = kw['request']
    values = [x.__name__ for x in _get_meetings(request)]
    return colander.OneOf(values)


class ExportMotionsSchema(colander.Schema):
    description = _("Export motions into a meeting. Each motion will be it's own agenda item.")
    meeting = colander.SchemaNode(
        colander.String(),
        title=_("Export to meeting"),
        widget=meetings_select_widget,
        validator=meetings_validator,
        description=_("export_meeting_schema_desc",
                      default="You must be moderator in the meeting you wish to export to.")
    )
    as_userid = colander.SchemaNode(
        colander.String(),
        title=_("Change all proposals to this user"),
        description=_("as_userid_schema_description",
                      default="If you want to override the default behaviour to "
                      "add proposals as the person who wrote them. "
                      "Not recommended unless you have a good reason to do so!"),
        missing="",
        widget=deferred_autocompleting_userid_widget,
    )
    view_perm = colander.SchemaNode(
        colander.Bool(),
        title=_("view_perm_schema_title",
                default="Give included users view permission "
                "within the meeting"),
        description=_("view_perm_schema_description",
                      default="If you're adding proposals as a specific user, "
                      "the original creators will get the view permission from this setting."),
        default=True,
    )


def includeme(config):
    config.add_schema('MotionProcess', MotionProcessSchema, ['add', 'edit'])
    config.add_schema('Motion', MotionSchema, ('add', 'edit'))
    config.add_schema('Motion', EditEndorsementsSchema, 'endorsements')
    config.add_schema('MotionProcess', ExportMotionsSchema, 'export_motions')

