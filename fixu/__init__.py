import os
from dotenv import load_dotenv
from flask import Flask, redirect, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extensions import db, migrate, login_manager, csrf
from .models import User
from flask_wtf.csrf import generate_csrf


def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Detrás de nginx solo hay UN proxy de confianza (el reverse proxy del
    # servidor público). Sin esto, request.remote_addr siempre es la IP
    # interna de nginx (misma para todos los usuarios), lo que rompe el
    # rate limiting por IP y cualquier lógica que dependa de la IP real.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Asegurar carpeta instance
    os.makedirs(app.instance_path, exist_ok=True)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)

    # Blueprints
    from .auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .tickets.routes import bp as tickets_bp
    app.register_blueprint(tickets_bp)

    from .teams.routes import bp as teams_bp
    app.register_blueprint(teams_bp)

    from .requesters.routes import bp as requesters_bp
    app.register_blueprint(requesters_bp)

    from .categories.routes import bp as categories_bp
    app.register_blueprint(categories_bp)

    from .agents.routes import bp as agents_bp
    app.register_blueprint(agents_bp)

    from .api.routes import bp as api_bp
    app.register_blueprint(api_bp)

    @app.route('/')
    def home():
        return redirect(url_for('tickets.index'))

    # Inyectar helper csrf_token() y URL de Laravel Admin en Jinja
    @app.context_processor
    def inject_globals():
        return dict(
            csrf_token=generate_csrf,
            laravel_admin_url=app.config.get('LARAVEL_ADMIN_URL', '')
        )

    # Evitar que el navegador cachee páginas autenticadas: sin esto, el botón
    # "atrás" puede mostrar una página de sesión iniciada (ej. panel de admin)
    # después de haber cerrado sesión.
    @app.after_request
    def no_cache_authenticated_pages(response):
        if not request.path.startswith('/static'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
        return response

    with app.app_context():
        if os.environ.get('FIXU_BOOTSTRAP_DB', '0') == '1':
            try:
                maybe_bootstrap_db()
            except Exception as e:
                import warnings
                warnings.warn(f"[Fixu] Bootstrap DB falló (puede ser normal en el primer arranque): {e}")
        register_commands(app)

    return app


def maybe_bootstrap_db():
    """Crea tablas y datos mínimos de desarrollo si la BD está vacía."""
    from .models import User, Team, TeamMember, Requester, Ticket, Category

    db.create_all()

    if not User.query.first():
        # Usuarios por defecto
        admin = User(name='Admin', email='admin@fixu.local', role='admin')
        admin.set_password('admin123')
        
        agent = User(name='Agente', email='agent@fixu.local', role='agent')
        agent.set_password('agent123')
        
        requester_user = User(name='Solicitante', email='requester@fixu.local', role='requester')
        requester_user.set_password('requester123')
        
        db.session.add_all([admin, agent, requester_user])
        db.session.commit()

        team = Team(name='Soporte')
        db.session.add(team)
        db.session.commit()

        member = TeamMember(user_id=agent.id, team_id=team.id)
        db.session.add(member)
        db.session.commit()

        requester = Requester(name='Solicitante', email='requester@fixu.local', phone='5551234567')
        db.session.add(requester)
        db.session.commit()

        ticket = Ticket(
            title='Ejemplo: No puedo iniciar sesión',
            body='Al intentar iniciar sesión recibo un error 500.',
            requester_id=requester.id,
            team_id=team.id,
            assignee_team_member_id=member.id,
            status='open',
            priority='medium',
            rating=0
        )
        db.session.add(ticket)
        db.session.commit()


def register_commands(app):
    import click
    from .models import User, Team, TeamMember, Requester, Ticket, Category

    @app.cli.command('seed')
    def seed():
        """Crea datos de ejemplo."""
        db.create_all()
        if not User.query.first():
            admin = User(name='Admin', email='admin@fixu.local', role='admin')
            admin.set_password('admin123')
            
            agent = User(name='Agente', email='agent@fixu.local', role='agent')
            agent.set_password('agent123')
            
            requester_user = User(name='Solicitante', email='requester@fixu.local', role='requester')
            requester_user.set_password('requester123')
            
            db.session.add_all([admin, agent, requester_user])
            db.session.commit()

            team = Team(name='Soporte')
            db.session.add(team)
            db.session.commit()

            member = TeamMember(user_id=agent.id, team_id=team.id)
            db.session.add(member)
            db.session.commit()

            requester = Requester(name='Solicitante', email='requester@fixu.local', phone='5551234567')
            db.session.add(requester)
            db.session.commit()

            ticket = Ticket(
                title='Ejemplo: No puedo iniciar sesión',
                body='Al intentar iniciar sesión recibo un error 500.',
                requester_id=requester.id,
                team_id=team.id,
                assignee_team_member_id=member.id,
                status='open',
                priority='medium',
                rating=0
            )
            db.session.add(ticket)
            db.session.commit()
        click.echo('Datos de ejemplo creados (si no existían).')

    @app.cli.command('create-admin')
    @click.option('--email', default='admin@fixu.local', show_default=True)
    @click.option('--password', default='admin123', show_default=True)
    @click.option('--name', default='Admin', show_default=True)
    def create_admin(email, password, name):
        """Crea o actualiza el usuario admin."""
        db.create_all()
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email, role='admin')
        user.name = name
        user.role = 'admin'
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin listo: {email}')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
