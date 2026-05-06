from flask import Flask, render_template, request, redirect, url_for


def create_app():
    app = Flask(__name__)

    import os
    import logging
    from .logging_config import JSONFormatter

    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-huskyhub-2024")

    log_dir = "/var/log/huskyhub"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(f"{log_dir}/app.log")
    file_handler.setFormatter(JSONFormatter())
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    from .routes.auth import auth_bp
    from .routes.grades import grades_bp
    from .routes.enrollment import enrollment_bp
    from .routes.messages import messages_bp
    from .routes.documents import documents_bp
    from .routes.admin import admin_bp
    from .routes.chatbot import chatbot_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(enrollment_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)

    @app.route("/")
    def home():
        username = request.cookies.get("authenticated")
        if not username:
            return redirect(url_for("auth.login"))
        role = request.cookies.get("role", "student")
        return render_template("home.html", username=username, role=role)

    @app.errorhandler(Exception)
    def handle_error(e):
        app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred."}, 500

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found."}, 404

    return app
