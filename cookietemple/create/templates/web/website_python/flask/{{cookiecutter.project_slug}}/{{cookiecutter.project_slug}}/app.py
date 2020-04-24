from .config import Config, config_mail, login, db, migrate, mail, bootstrap, babel
from flask import Flask, request, session
import click
import os
from flask import Flask
{ % if cookiecutter.is_basic_website == 'y' - %}
{ % endif % }
{ % if cookiecutter.is_basic_website == 'n' - %}
{ % endif % }
{ % if cookiecutter.is_basic_website == 'y' - %}
from .config import Config{ % endif % }

app = Flask(__name__)
app.config.from_object(Config)
{ % if cookiecutter.is_basic_website == 'n' - %}
migrate.init_app(app, db)
login.init_app(app)
mail.init_app(app)
bootstrap.init_app(app)
babel.init_app(app)

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

config_mail(app){ % endif % }

from {{cookiecutter.project_slug}}.errors import bp as errors_bp  # noqa: E402

app.register_blueprint(errors_bp)

{ % if cookiecutter.is_basic_website == 'y' - %}
from {{cookiecutter.project_slug}}.basic import bp as basic_bp  # noqa: E402

app.register_blueprint(basic_bp)
{ % endif % }

{ % if cookiecutter.is_basic_website == 'n' - %}
from {{cookiecutter.project_slug}}.auth import bp as auth_bp  # noqa: E402

app.register_blueprint(auth_bp, url_prefix='/auth')

from {{cookiecutter.project_slug}}.main import bp as main_bp  # noqa: E402

app.register_blueprint(main_bp)


@app.cli.group()
def translate():
    """Translation commands"""
    pass


@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language"""
    if os.system('pybabel extract -F babel.cfg -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel init -i messages.pot -d {{cookiecutter.project_slug}}/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')


@translate.command()
def update():
    """Update all languages"""

    if os.system('pybabel extract -F babel.cfg -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d {{cookiecutter.project_slug}}/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')


@translate.command()
def compile():
    """Compile all languages"""

    if os.system('pybabel compile -d {{cookiecutter.project_slug}}/translations'):
        raise RuntimeError('compile command failed')


"""This selector checks, if the user selected a language manually and in that case uses this language for translations.
    However, if the user has not selected any language (when accessing the page for the first time, new browser session,
    ...) it will choose the best matching language out of the configured ones, using browser settings and request headers
    "Accept-Language:" property
"""


@babel.localeselector
def get_locale():
    # if the user has set up the language manually it will be stored in the session,
    # so we use the locale from the user settings
    try:
        language = session['language']
    except KeyError:
        language = None
    if language is not None:
        return language
    return request.accept_languages.best_match(Config.LANGUAGES.keys())


"""This function allows us to use all possible language options and the current language in our templates"""


@app.context_processor
def inject_conf_var():
    return dict(
        AVAILABLE_LANGUAGES=Config.LANGUAGES,
        CURRENT_LANGUAGE=session.get('language', request.accept_languages.best_match(Config.LANGUAGES.keys()))){ % endif % }
