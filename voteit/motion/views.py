from arche.views.base import BaseView
from arche.views.base import DefaultEditForm
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.traversal import find_interface
from pyramid.view import view_config
from pyramid.view import view_defaults
from voteit.core.security import CHANGE_WORKFLOW_STATE
from voteit.core.security import EDIT
from voteit.core.security import VIEW
from webhelpers.html.converters import nl2br
from webhelpers.html.render import sanitize
from webhelpers.html.tools import auto_link

from voteit.motion import _
from voteit.motion.intefaces import IMotion
from voteit.motion.intefaces import IMotionProcess
from voteit.motion.permissions import ADD_MOTION, ENDORSE_MOTION
from voteit.motion.permissions import CHECK_EMAIL_AGAINST_HASHLIST
from voteit.motion.permissions import ENABLE_MOTION_SHARING
from voteit.motion.security import ROLE_MOTION_PROCESS_PARTICIPANT


@view_config(context=IMotionProcess,
             name='view',
             permission=VIEW,
             renderer='voteit.motion:templates/motion_process.pt')
class MotionProcessView(BaseView):

    def __call__(self):
        return {'can_add_motion':  self.request.has_permission(ADD_MOTION, self.context),
                'check_email_snippet': render_check_email_snippet(self.context, self.request)}

    def get_motions(self):
        for obj in self.context.values():
            if IMotion.providedBy(obj) and self.request.has_permission(VIEW, obj):
                yield obj


@view_config(context=IMotion,
             name='edit_endorsements',
             permission=EDIT,
             renderer='arche:templates/form.pt')
class EditEndorsementsForm(DefaultEditForm):
    schema_name = 'endorsements'


@view_defaults(
    context=IMotion,
    renderer='voteit.motion:templates/motion.pt')
class MotionView(BaseView):

    @view_config(name='view', permission=VIEW)
    def main_view(self):
        can_submit = self.context.wf_state == 'draft' and \
                     self.request.has_permission(CHANGE_WORKFLOW_STATE, self.context)
        return {'can_submit': can_submit,
                'can_edit': self.request.has_permission(EDIT, self.context),
                'can_endorse': self.request.authenticated_userid not in self.context.creator and
                               self.request.has_permission(ENDORSE_MOTION, self.context),
                'can_enable_sharing': ENABLE_MOTION_SHARING,
                'check_email_snippet': render_check_email_snippet(self.context, self.request)}

    @view_config(name='_ts', permission=NO_PERMISSION_REQUIRED)
    def token_view(self):
        if not self.context.sharing_token:
            raise HTTPNotFound()
        if self.request.subpath and self.request.subpath[0] == self.context.sharing_token:
            return self.main_view()
        raise HTTPNotFound()

    def format_text(self, text):
        text = sanitize(text)
        text = auto_link(text)
        return nl2br(text)

    @view_config(name="toggle_sharing", permission=ENABLE_MOTION_SHARING)
    def toggle_sharing(self):
        state = self.request.GET.get('s', None)
        if state == 'on':
            self.context.enable_sharing_token()
            self.flash_messages.add(_("sharing_switched_on",
                                      default="Sharing enalbed - use the link below."),
                                    type='success')
        if state == 'off':
            self.context.remove_sharing_token()
            self.flash_messages.add(_("sharing_switched_off",
                                      default="Sharing switched off - motion not accessible unless you're logged in."),
                                    type='warning')
        return HTTPFound(location=self.request.resource_url(self.context))

    @view_config(name="endorsement", permission=ENDORSE_MOTION)
    def set_endorsement(self):
        state = self.request.GET.get('s', None)
        came_from = self.request.GET.get('came_from', None)
        endorsements = set(self.context.endorsements)
        userid = self.request.authenticated_userid
        if state == 'yes':
            if userid not in endorsements:
                endorsements.add(userid)
                self.context.endorsements = endorsements
            self.flash_messages.add(_("youre_now_endorsing",
                                      default="You're now endorsing this motion."),
                                    type='success')
        if state == 'no':
            if userid in endorsements:
                endorsements.remove(userid)
                self.context.endorsements = endorsements
            self.flash_messages.add(_("your_endorsement_removed",
                                      default="You're no longer endorsing this motion."),
                                    type='warning')
        if came_from:
            return HTTPFound(location=came_from)
        return HTTPFound(location=self.request.resource_url(self.context))


@view_config(
    context=IMotionProcess,
    name='check_email',
    permission=CHECK_EMAIL_AGAINST_HASHLIST)
class CheckAgainstHashlistView(BaseView):

    def __call__(self):
        profile = self.request.profile
        if not profile:
            raise HTTPForbidden(_("Must be logged in"))
        if not profile.email or not profile.email_validated:
            raise HTTPForbidden(_("no_validated_email_error",
                                  default="You need to have a validated email address to use this. "
                                  "Validate your email on the profile page."))
        came_from = self.request.GET.get('came_from', None)
        if came_from:
            response = HTTPFound(location=came_from)
        else:
            response = HTTPFound(location=self.request.resource_url(self.context))
        for uid in self.context.hashlist_uids:
            hashlist = self.request.resolve_uid(uid, perm=None)
            res = hashlist.check(profile.email)
            if res == True:
                self.context.local_roles.add(profile.userid, ROLE_MOTION_PROCESS_PARTICIPANT)
                self.flash_messages.add(_("granted_access_message",
                                          default="You've been granted access to add motions "
                                          "(if process is open) and to endorse motions"),
                                        type="success", auto_destruct=False)
                return response
        self.flash_messages.add(_("not_found_when_checked_against_hashlist",
                                  default="We couldn't find your email address. "
                                          "Please contact the organisation responsible for this process to gain access."),
                                type='danger',
                                auto_destruct=False)
        return response


def render_check_email_snippet(context, request):
    mp = find_interface(context, IMotionProcess)
    if not mp.hashlist_uids:
        #Nothing to do
        return ''
    if request.profile is None:
        return ''
    already_has_role = ROLE_MOTION_PROCESS_PARTICIPANT in mp.local_roles.get(request.authenticated_userid, ())
    values = {'context': context,
              'can_check': request.has_permission(CHECK_EMAIL_AGAINST_HASHLIST, mp) and
                           not already_has_role,
              'check_url': request.resource_url(mp, 'check_email',
                                                query={'came_from': request.resource_url(context)})}
    return render('voteit.motion:templates/check_email.pt', values, request=request)


def includeme(config):
    config.scan(__name__)
