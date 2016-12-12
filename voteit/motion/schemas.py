from __future__ import unicode_literals

import colander
import deform
from arche.widgets import deferred_autocompleting_userid_widget, ReferenceWidget
#from voteit.core.schemas.common import strip_and_lowercase

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
        description=_("motion_process_schema_description",
                      default="Short description, visible as lead-in and on searches.")
    )
    body = colander.SchemaNode(
        colander.String(),
        title=_("Text body"),
        missing="",
        description=_("Describe the process etc..."),
        widget=deform.widget.RichTextWidget(),
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
        description=_("motion_schema_description",
                      default="Visible as lead-in and on searches. Keep it very short!")
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
        title=_("Proposals add at least one"),
        description=_("motion_proposals_schema_description",
                      default="Proposals must be written in a way so it's possible to approve or deny each one. "
                              "Don't give any background information or similar here."),
        widget=deform.widget.SequenceWidget(orderable=True),
        default=[''],
        validator=colander.Length(min=1,)
    )


# class MotionInviteSchema(colander.Schema):
#     emails = colander.SchemaNode(
#         colander.Sequence(),
#         colander.SchemaNode(
#             colander.String(),
#             name='not_used',
#             title=_("Email"),
#             validator=colander.Email(),
#             preparer=strip_and_lowercase,
#         ),
#         title=_("Email addresses to send invitation to"),
#         widget=deform.widget.SequenceWidget(orderable=True),
#         default=[''],
#     )


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
        title=_("Written endorsements"),
        description=_("From non-users."),
        missing="",
        widget=deform.widget.RichTextWidget(height=200),
    )


def includeme(config):
    config.add_schema('MotionProcess', MotionProcessSchema, ['add', 'edit'])
    config.add_schema('Motion', MotionSchema, ('add', 'edit'))
    #config.add_schema('Motion', MotionInviteSchema, 'invite')
    config.add_schema('Motion', EditEndorsementsSchema, 'endorsements')
