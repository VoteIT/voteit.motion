from arche.fanstatic_lib import common_js
from arche.interfaces import IBaseView
from arche.interfaces import IViewInitializedEvent
from fanstatic import Library
from fanstatic import Resource
from js.bootstrap import bootstrap_js
from js.bootstrap import bootstrap_css


library = Library('voteit_motion', 'static')

voteitmotion_css = Resource(library, 'css/main.css', depends = (bootstrap_css,))


def need_subscriber(view, event):
    voteitmotion_css.need()


def includeme(config):
    config.add_subscriber(need_subscriber, [IBaseView, IViewInitializedEvent])
