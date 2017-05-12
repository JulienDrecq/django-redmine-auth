**Django Redmine Auth**

======================================

Django app for **Redmine** authentication.


Application development and testing with django v1.10, Redmine v3.3.1


.. contents:: Contents
    :depth: 2
    
Requirements
-----------

1. Add lib python-redmine => https://github.com/maxtepkeev/python-redmine


Quick start
-----------

1. Add ``redmine_auth`` to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'redmine_auth',
      )

2. Add ``backend`` to your AUTHENTICATION_BACKENDS setting like this::

    AUTHENTICATION_BACKENDS = (
        ...
        'redmine_auth.backends.RedmineBackend',
    )
    
3. Edit the information to connect to your server Redmine in ``redmine_auth/settings.py`` ::

    REDMINE_SERVER_URL = getattr(settings, 'REDMINE_SERVER_URL', 'http://localhost')

4. Run ``python manage.py syncdb`` to create the redmine_auth models.

5. For call ``redmine_auth``, use standard authenticate ::

    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)

6. Access in template to ``redmine_auth`` ::

    {{ user.redmineuser.redmine_user_id }}
    {{ user.redmineuser.username }}

7. Also accessing built-in model ``User`` can be used.

    {{ user.username }} -- equals to user.redmineuser.username
    {{ user.first_name }}
    {{ user.last_name }}
    {{ user.email }} -- may be blank, depend on personal settings

8. (Optional) For allowing users which belong to specified projects,
   add REDMINE_AUTHZ_PROJECTS to your ``settings.py``  like this::

    REDMINE_AUTHZ_PROJECTS = ('test-proj',)
    
Contributors
-----------
   * Julien Drecq ( https://github.com/JulienDrecq/ )
   * eisin ( https://github.com/eisin )
