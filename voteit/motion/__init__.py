from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('voteit.motion')


def includeme(config):
    config.include('.fanstatic_lib')
    config.include('.resources')
    config.include('.security')
    config.include('.schemas')
    config.include('.views')
    config.include('.workflows')
    #Static dir
    config.add_static_view('static_voteitmotion', 'static', cache_max_age=3600)
    #Translations
    config.add_translation_dirs('voteit.motion:locale/')
