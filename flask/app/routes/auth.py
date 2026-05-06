from flask import (
    Blueprint, request, redirect, url_for,
    render_template, make_response, current_app
)
from ..database import get_connection
from ..utils import hash_password, check_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch user by username only — password comparison happens in Python
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND approved = 1",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password(password, user["password"]):
            current_app.logger.info(
                "Successful login",
                extra={"user": username, "endpoint": "/login"}
            )
            resp = make_response(redirect(url_for("home")))
            # Store identity in cookies so the app knows who is logged in
            resp.set_cookie("authenticated", username)
            resp.set_cookie("role", user["role"])
            resp.set_cookie("user_id", str(user["user_id"]))
            return resp
        else:
            current_app.logger.warning(
                f"Failed login attempt for username: {username}",
                extra={"user": username, "endpoint": "/login"}
            )
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    resp = make_response(redirect(url_for("auth.login")))
    resp.delete_cookie("authenticated")
    resp.delete_cookie("role")
    resp.delete_cookie("user_id")
    return resp


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        first_name = request.form.get("first_name", "")
        last_name = request.form.get("last_name", "")
        email = request.form.get("email", "")

        # Hash the password before storing it
        hashed = hash_password(password)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users "
                "(username, first_name, last_name, email, password, role, approved) "
                "VALUES (%s, %s, %s, %s, %s, 'student', 0)",
                (username, first_name, last_name, email, hashed)
            )
            conn.commit()
            return redirect(url_for("auth.login"))
        except Exception as e:
            error = f"Registration error: {str(e)}"
        finally:
            conn.close()

    return render_template("register.html", error=error)
