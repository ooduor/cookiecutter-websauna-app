"""Create virtualenv and print a thank you note."""
from textwrap import dedent
import binascii
import os
import subprocess
import sys

try:
    import secrets
    HAS_SECRETS = True
except ImportError:
    HAS_SECRETS = False

try:
    import venv
    VIRTUALENV_AVAILABLE = True
except ImportError:
    VIRTUALENV_AVAILABLE = False


def compat_token_hex() -> str:
    """Return a token_hex with 20 bytes."""
    if HAS_SECRETS:
        value = secrets.token_hex(20)
    else:
        value = binascii.hexlify(os.urandom(20)).decode('utf-8')
    return value


SECRET_FILES = (
    'development-secrets.ini',
    'production-secrets.ini',
    'staging-secrets.ini',
    'test-secrets.ini',
)


SECRET_VARS = (
    (r'%cookiecutter.authentication_random%', compat_token_hex()),
    (r'%cookiecutter.authomatic_random%', compat_token_hex()),
    (r'%cookiecutter.session_random%', compat_token_hex()),
)


create_virtualenv = True if '{{ cookiecutter.create_virtualenv }}' == 'Yes' else False


if VIRTUALENV_AVAILABLE and create_virtualenv:
    try:
        venv.create('env', with_pip=True)
        proc = subprocess.Popen(
            ['env/bin/pip', 'install', '-r', 'requirements.txt'],
            shell=sys.platform.startswith('win'),
            cwd='.'
        )
        proc.wait()
    except subprocess.CalledProcessError:
        print('It was not possible to create the virtualenv. Maybe inside tox?')
    except FileNotFoundError as e:
        print(subprocess.check_output(['ls', './env/bin/']), str(e))


for filename in SECRET_FILES:
    path = './{{ cookiecutter.namespace }}/{{ cookiecutter.package_name }}/conf/{filename}'.format(
        filename=filename
    )
    with open(path, 'r+') as fh:
        content = fh.read()
        for placeholder, value in SECRET_VARS:
            content = content.replace(placeholder, value)
        fh.seek(0,0)
        fh.write(content)


msg = dedent("""
    ===============================================================================
    Websauna Application.
    Package {{ cookiecutter.repo_name }} was generated.
    Now, code it, create a git repository, push to your Github account.
    To deploy this Websauna package with Ansible, use the following variables

        - package_name: {{ cookiecutter.repo_name }}
        - package_path: {{ cookiecutter.namespace }}/{{ cookiecutter.package_name }}

    Read more about Websauna deployment:
      https://websauna.org/docs/tutorials/deployment/index.html

    Sorry for the convenience.
    ===============================================================================
""")

print(msg)
