from flask import Flask, request, redirect, url_for, session

app = Flask(__name__)

# Required for Flask sessions
app.secret_key = "broken-access-control-lab-secret-key"


# Simple user database
users = {
    "alice": {
        "password": "alice123",
        "user_id": 1,
        "name": "Alice",
        "role": "student",
        "email": "alice@test.com",
        "cgpa": "3.75"
    },
    "bob": {
        "password": "bob123",
        "user_id": 2,
        "name": "Bob",
        "role": "student",
        "email": "bob@test.com",
        "cgpa": "3.92"
    },
    "admin": {
        "password": "admin123",
        "user_id": 3,
        "name": "Admin",
        "role": "admin",
        "email": "admin@test.com",
        "cgpa": "N/A"
    }
}


@app.route("/")
def home():
    return """
    <h1>Student Profile Portal</h1>
    <p>OWASP A01:2025 Broken Access Control Lab</p>
    <p><a href="/login">Login</a></p>
    """


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = users.get(username)

        if user and user["password"] == password:

            session["username"] = username
            session["user_id"] = user["user_id"]

            return redirect(url_for("dashboard"))

        return """
        <h2>Login Failed</h2>
        <p>Invalid username or password.</p>
        <a href="/login">Try Again</a>
        """

    return """
    <h1>Login</h1>

    <form method="POST">

        <label>Username:</label><br>
        <input type="text" name="username"><br><br>

        <label>Password:</label><br>
        <input type="password" name="password"><br><br>

        <button type="submit">Login</button>

    </form>
    """


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user = users[username]

    return f"""
    <h1>Student Dashboard</h1>

    <p>Welcome, <strong>{user["name"]}</strong></p>

    <p>Role: {user["role"]}</p>

    <p>
        <a href="/profile/{user["user_id"]}">
            View My Profile
        </a>
    </p>

    <p>
        <a href="/logout">
            Logout
        </a>
    </p>
    """


# Vulnerable profile page
# This intentionally contains a Broken Access Control / IDOR vulnerability
@app.route("/profile/<int:user_id>")
def profile(user_id):

    # User must be logged in
    if "username" not in session:
        return redirect(url_for("login"))

    selected_user = None

    # Find the user based on the ID entered in the URL
    for username, user in users.items():

        if user["user_id"] == user_id:
            selected_user = user
            break

    if selected_user is None:
        return "User not found", 404

    # VULNERABILITY:
    # We do NOT check whether the logged-in user
    # is actually allowed to access this profile.

    return f"""
    <h1>Student Profile</h1>

    <p><strong>Name:</strong> {selected_user["name"]}</p>
    <p><strong>User ID:</strong> {selected_user["user_id"]}</p>
    <p><strong>Email:</strong> {selected_user["email"]}</p>
    <p><strong>CGPA:</strong> {selected_user["cgpa"]}</p>
    <p><strong>Role:</strong> {selected_user["role"]}</p>

    <br>

    <a href="/dashboard">Back to Dashboard</a>
    """


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)