from __future__ import unicode_literals

import colander
import deform
from arche.widgets import deferred_autocompleting_userid_widget, ReferenceWidget

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


def includeme(config):
    config.add_schema('MotionProcess', MotionProcessSchema, ['add', 'edit'])
    config.add_schema('Motion', MotionSchema, ('add', 'edit'))
    config.add_schema('Motion', EditEndorsementsSchema, 'endorsements')
