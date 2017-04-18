import colander
import deform
from arche.interfaces import ISchemaCreatedEvent
from pyramid.httpexceptions import HTTPForbidden
from voteit.core.security import ADD_PROPOSAL
from voteit.core.security import VIEW

from voteit.motion import _
from voteit.motion.plugins.preprocess.utils import get_portlet


class OptionItem(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title=_("ID of the option"),
        description=_("Use only lowercase + numbers, no spaces")
    )
    title = colander.SchemaNode(
        colander.String(),
        title=_("Readable title")
    )


TAG_WIDGETS = {
    'checkbox': deform.widget.CheckboxChoiceWidget,
    'radio': deform.widget.RadioChoiceWidget,
}

TAG_WIDGET_TITLES = {
    'checkbox': _("Checkboxes (Multiple options, type: Set)"),
    'radio': _("Radio buttons (Single option, type: String)"),
}

TAG_WIDGET_DATA_TYPE = {
    'checkbox': colander.Set,
    'radio': colander.String,
}


class OptionItems(colander.SequenceSchema):
    items = OptionItem()


class PreprocessPortletSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        title=_("Title"),
    )
    body = colander.SchemaNode(
        colander.String(),
        title=_("Body"),
        widget=deform.widget.RichTextWidget(),
    )
    button_caption = colander.SchemaNode(
        colander.String(),
        title=_("Button caption"),
        default=_("Add tag(s)"),
    )
    form_title = colander.SchemaNode(
        colander.String(),
        title=_("Form title, for the modal window"),
    )
    form_description = colander.SchemaNode(
        colander.String(),
        title=_("Form description text, for the modal window"),
        widget=deform.widget.RichTextWidget(),
        default="",
        missing="",
    )
    tags_selectable = OptionItems(
        widget=deform.widget.SequenceWidget(orderable=True)
    )
    tags_widget = colander.SchemaNode(
        colander.String(),
        title=_("The widget users select tags with"),
        description=_("tags_widget_description",
                      default="Note! Once the process have started, you can't change widget "
                              "between different types. "
                              "That would cause the saved result to break."),
        widget=deform.widget.RadioChoiceWidget(
            values=[(k, v) for (k, v) in TAG_WIDGET_TITLES.items()])
    )
    tags_perm = colander.SchemaNode(
        colander.String(),
        title=_("Require the following perm to tag"),
        description=_(
            "tags_perm_description",
            default="'${add_prop}' is a sensible default value. For everyone, use '${view}'",
            mapping={'add_prop': ADD_PROPOSAL, 'view': VIEW}
        ),
        default=ADD_PROPOSAL,
        missing=ADD_PROPOSAL
    )
    process_open = colander.SchemaNode(
        colander.Bool(),
        title=_("Is the process open?")
    )
    icon = colander.SchemaNode(
        colander.String(),
        title = _("Icon CSS classes"),
        default = "glyphicon glyphicon-tags",
        missing = "",
    )


@colander.deferred
def picked_tags_widget(node, kw):
    portlet = kw['portlet']
    settings = portlet.settings
    values=[(x['name'], x['title']) for x in settings['tags_selectable']]
    Widget = TAG_WIDGETS.get(settings.get('tags_widget', ''), None)
    if Widget is None:
        raise HTTPForbidden("Widget not found")
    return Widget(values=values)


@colander.deferred
def deferred_modal_form_description(node, kw):
    portlet = kw['portlet']
    return portlet.settings.get('form_description', '')


@colander.deferred
def deferred_modal_form_title(node, kw):
    portlet = kw['portlet']
    return portlet.settings.get('form_title', '')


class TagFormSchema(colander.Schema):
    title = deferred_modal_form_title
    widget = deform.widget.FormWidget(
        template='form_modal',
        readonly_template='readonly/form_modal'
    )
    description = deferred_modal_form_description


def insert_tags_node(schema, event):
    portlet_uid = event.request.GET.get('portlet', '')
    portlet = get_portlet(event.request, portlet_uid)
    DataType = TAG_WIDGET_DATA_TYPE.get(portlet.settings.get('tags_widget', ''), None)
    if not DataType:
        raise HTTPForbidden("Portlet has bad configuration")
    schema.add(
        colander.SchemaNode(
            DataType(),
            title = _("Choose"),
            widget=picked_tags_widget,
            name='tags',
        )
    )


def includeme(config):
    config.add_schema('AgendaItem', TagFormSchema, 'preprocess_tags')
    config.add_subscriber(insert_tags_node, [TagFormSchema, ISchemaCreatedEvent])
