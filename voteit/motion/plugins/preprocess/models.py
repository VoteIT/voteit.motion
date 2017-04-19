from arche.utils import AttributeAnnotations
from six import string_types
from voteit.core.models.interfaces import IAgendaItem
from zope.component import adapter
from zope.interface import implementer

from voteit.motion.plugins.preprocess.interfaces import IPreprocessUserTags


@adapter(IAgendaItem)
@implementer(IPreprocessUserTags)
class PreprocessUserTags(AttributeAnnotations):
    attr_name = '_preprocess_user_tags'

    def get_results(self):
        results = {}
        for row in self.values():
            if isinstance(row, string_types):
                results.setdefault(row, 0)
                results[row] += 1
            else:
                for k in row:
                    results.setdefault(k, 0)
                    results[k] += 1
        return results


def includeme(config):
    config.registry.registerAdapter(PreprocessUserTags)
