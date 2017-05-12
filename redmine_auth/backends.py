from django.contrib.auth.models import User, Group
from django.conf import settings
from redmine_auth.models import RedmineUser
from redmine_auth.settings import *
from redmine import Redmine
from redmine.exceptions import AuthError, ResourceAttrError
import logging
logger = logging.getLogger(__name__)


class RedmineBackend(object):

    def authenticate(self, username=None, password=None):
        user = None
        redmine_projects_identifier = []
        try:
            redmine = Redmine(settings.REDMINE_SERVER_URL, username=username, password=password)
            redmine_user = redmine.user.get("current", include="memberships")
            for membership in redmine_user.memberships:
                redmine_projects_identifier.append(redmine.project.get(membership.project.id).identifier)
            if not self._check_redmine_project(redmine, redmine_projects_identifier):
                logger.error('Exeption with Redmine authentificate. User does not belong to specified groups.')
                return None
            
            try:
                django_redmine_user = RedmineUser.objects.get(redmine_user_id=redmine_user.id)
                if django_redmine_user.username != username:
                    django_redmine_user.username = username
                    django_redmine_user.save()
                user = django_redmine_user.user
                if self._refresh_user(redmine_user, user, username, redmine_projects_identifier):
                    user.save()
            except RedmineUser.DoesNotExist:
                user, created = User.objects.get_or_create(username=username)
                self._refresh_user(redmine_user, user, username, redmine_projects_identifier)
                user.save()
                django_redmine_user = RedmineUser(user=user, username=username, redmine_user_id=redmine_user.id)
                django_redmine_user.save()
        except AuthError:
            logger.error('Exception with Redmine authentificate. Username or password invalid.')
            return None
        return user

    def get_user(self, user_id):
        try:
            return RedmineUser.objects.get(user=user_id).user
        except RedmineUser.DoesNotExist:
            logger.error('No Redmine user identified with id : %s' % user_id)
            return None

    def _refresh_user(self, redmine_user, user, username, redmine_projects_identifier):
        has_changed = False
        if user.first_name != redmine_user.firstname:
            user.first_name = redmine_user.firstname
            has_changed = True
        if user.last_name != redmine_user.lastname:
            user.last_name = redmine_user.lastname
            has_changed = True
        if user.username != username:
            user.username = username
            has_changed = True
        try:
            if user.email != redmine_user.mail:
                user.email = redmine_user.mail
                has_changed = True
        except ResourceAttrError:
            # email address can be hidden
            pass

        authz_projects = getattr(settings, "REDMINE_AUTHZ_PROJECTS", None)
        authz_group_prefix = getattr(settings, "REDMINE_AUTHZ_GROUP_PREFIX", "redmine_")
        if not authz_projects is None:
            for project_alphabet_identifier in redmine_projects_identifier:
                if project_alphabet_identifier in authz_projects:
                    # need to assign specified group
                    group, created = Group.objects.get_or_create(name=authz_group_prefix + project_alphabet_identifier)
                    if not user.groups.filter(name=group.name):
                        user.groups.add(group)
                        has_changed = True
                else:
                    # need to de-assign specified group
                    try:
                        group = Group.objects.get(name=authz_group_prefix + project_alphabet_identifier)
                        if user.groups.filter(name=group.name):
                            user.groups.remove(group)
                            has_changed = True
                    except Group.DoesNotExist:
                        pass
        return has_changed

    def _check_redmine_project(self, redmine, redmine_projects_identifier):
        authz_projects = getattr(settings, "REDMINE_AUTHZ_PROJECTS", None)
        if authz_projects is None:
            # Don't use project authorization
            return True

        for project_alphabet_identifier in redmine_projects_identifier:
            if project_alphabet_identifier in authz_projects:
                return True

        return False
