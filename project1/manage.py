#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    print('ngrok http --domain=engaging-mastodon-accurate.ngrok-free.app 8080')
    print('http://localhost/users/telegram/callback/?id=7390715192&first_name=Platon&last_name=Cross&username=platon_cross&auth_date=1723746975&hash=e1a2cd49dd85aa71ce5edf003f3a358103fcecca0bb7e15dec78c7a7bc3e8fa4')
    print('pagekite 8000 jahoroshi4y.pagekite.me')
    main()
