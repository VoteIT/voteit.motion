from __future__ import unicode_literals

import colander
import deform
from arche.widgets import deferred_autocompleting_userid_widget

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


class AddMotionSchema(colander.Schema):
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


class MotionProposalsSchema(colander.Schema):
    proposals = colander.SchemaNode(
        colander.Sequence(),
        colander.SchemaNode(
            colander.String(),
            name='not_used',
            title=_("Proposal")
        ),
        title=_("Proposals"),
        description=_("motion_proposals_schema_description",
                      default="Proposals must be written in a way so it's possible to approve or deny each one. "
                              "Don't give any background information or similar here."),
        widget=deform.widget.SequenceWidget(orderable=True),
    )


class MotionInviteSchema(colander.Schema):
    pass


class EditMotionSchema(MotionProposalsSchema, AddMotionSchema):
    pass


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
    config.add_schema('Motion', AddMotionSchema, 'add')
    config.add_schema('Motion', MotionProposalsSchema, 'proposals')
    config.add_schema('Motion', MotionInviteSchema, 'invite')
    # remove schema view
    config.add_schema('Motion', EditMotionSchema, ('edit', 'view'))
    config.add_schema('Motion', EditEndorsementsSchema, 'endorsements')
