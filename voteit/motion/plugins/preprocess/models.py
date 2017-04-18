from arche.utils import AttributeAnnotations
from voteit.core.models.interfaces import IAgendaItem
from zope.component import adapter
from zope.interface import implementer

from voteit.motion.plugins.preprocess.interfaces import IPreprocessUserTags


@adapter(IAgendaItem)
@implementer(IPreprocessUserTags)
class PreprocessUserTags(AttributeAnnotations):
    attr_name = '_preprocess_user_tags'


def includeme(config):
    config.registry.registerAdapter(PreprocessUserTags)
