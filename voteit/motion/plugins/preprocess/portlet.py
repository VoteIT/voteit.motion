from __future__ import unicode_literals

from arche.portlets import PortletType
from pyramid.renderers import render

from voteit.motion import _
from voteit.motion.plugins.preprocess.schemas import PreprocessPortletSchema


class PreprocessPortlet(PortletType):
    name = "preprocess_motion"
    schema_factory = PreprocessPortletSchema
    title = _("Preprocess Motion")
    tpl = "voteit.motion.plugins.preprocess:templates/portlet.pt"

    def render(self, context, request, view, **kwargs):
        settings = self.portlet.settings
        response = {'title': settings.get('title', self.title),
                    'body': settings.get('body', ''),
                    'portlet': self.portlet,
                    'context': context,
                    'can_add': self.is_open(context, request),
                    'view': view,
                    'icon_cls': settings.get('icon', '')}
        return render(self.tpl,
                      response,
                      request = request)

    def is_open(self, context, request):
        settings = self.portlet.settings
        return settings.get('process_open', False) and \
               request.has_permission(settings.get('tags_perm', object()), context)

    def get_tags(self):
        return dict(
            [(x['name'], x['title']) for x in self.portlet.settings.get('tags_selectable', ())]
        )


def includeme(config):
    config.add_portlet(PreprocessPortlet)
