"""
VK Son Creative Studio — Flask Backend with PostgreSQL (Supabase)
Run: python app.py
"""

from flask import Flask, request, jsonify, send_file
import os, hashlib
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

app = Flask(__name__, static_folder=".", static_url_path="")

# ─── CONFIG ───────────────────────────────────────────
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:YOUR_PASSWORD_HERE@db.lpirqhjhvnkfrhgirgdh.supabase.co:5432/postgres"
)
ADMIN_USER   = "vkson_admin"
ADMIN_PASS   = "VKSon@2025!"
SECRET_TOKEN = "vkson_secret_2025"

# ─── DB HELPERS ───────────────────────────────────────
@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id         SERIAL PRIMARY KEY,
                title      TEXT NOT NULL,
                platform   TEXT DEFAULT 'youtube',
                link       TEXT NOT NULL,
                thumb      TEXT DEFAULT '',
                desc       TEXT DEFAULT '',
                category   TEXT DEFAULT 'general',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id      SERIAL PRIMARY KEY,
                name    TEXT NOT NULL,
                email   TEXT NOT NULL,
                phone   TEXT DEFAULT '',
                service TEXT DEFAULT '',
                message TEXT NOT NULL,
                time    TEXT,
                read    TEXT DEFAULT 'false'
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id         SERIAL PRIMARY KEY,
                author     TEXT NOT NULL,
                role       TEXT DEFAULT '',
                stars      TEXT DEFAULT '5',
                text       TEXT NOT NULL,
                visible    TEXT DEFAULT 'true',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS users (
                id        SERIAL PRIMARY KEY,
                name      TEXT NOT NULL,
                email     TEXT UNIQUE NOT NULL,
                pass_hash TEXT NOT NULL,
                joined    TEXT
            );

            CREATE TABLE IF NOT EXISTS vreviews (
                id       SERIAL PRIMARY KEY,
                video_id TEXT NOT NULL,
                user_id  TEXT NOT NULL,
                author   TEXT DEFAULT 'Anonymous',
                stars    TEXT NOT NULL,
                text     TEXT NOT NULL,
                time     TEXT
            );
        """)
    print("✅ Database ready!")

def now():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ─── CORS ─────────────────────────────────────────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(path):
        return send_file(path)
    return send_file("index.html")

# ─── AUTH HELPER ──────────────────────────────────────
def check_admin(req):
    token = req.headers.get("Authorization", "").replace("Bearer ", "")
    return token == SECRET_TOKEN

# ════════════════════════════════════════════════════════
#  ADMIN AUTH
# ════════════════════════════════════════════════════════
@app.route("/api/admin/login", methods=["POST", "OPTIONS"])
def admin_login():
    if request.method == "OPTIONS": return jsonify({}), 200
    d = request.json or {}
    if d.get("username") == ADMIN_USER and d.get("password") == ADMIN_PASS:
        return jsonify({"ok": True, "token": SECRET_TOKEN})
    return jsonify({"ok": False, "error": "Invalid credentials"}), 401


# ════════════════════════════════════════════════════════
#  USER AUTH
# ════════════════════════════════════════════════════════
@app.route("/api/users/signup", methods=["POST", "OPTIONS"])
def user_signup():
    if request.method == "OPTIONS": return jsonify({}), 200
    d     = request.json or {}
    name  = d.get("name","").strip()
    email = d.get("email","").strip().lower()
    pwd   = d.get("password","")

    if not name or not email or not pwd:
        return jsonify({"ok": False, "error": "All fields required"}), 400
    if len(pwd) < 6:
        return jsonify({"ok": False, "error": "Password min 6 chars"}), 400

    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, email, pass_hash, joined) VALUES (%s,%s,%s,%s) RETURNING id,name,email",
                (name, email, hash_pass(pwd), now())
            )
            user = dict(cur.fetchone())
        return jsonify({"ok": True, "user": user})
    except psycopg2.errors.UniqueViolation:
        return jsonify({"ok": False, "error": "Email already registered"}), 409

@app.route("/api/users/login", methods=["POST", "OPTIONS"])
def user_login():
    if request.method == "OPTIONS": return jsonify({}), 200
    d     = request.json or {}
    email = d.get("email","").strip().lower()
    pwd   = d.get("password","")
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id,name,email FROM users WHERE email=%s AND pass_hash=%s",
            (email, hash_pass(pwd))
        )
        user = cur.fetchone()
    if not user:
        return jsonify({"ok": False, "error": "Invalid email or password"}), 401
    return jsonify({"ok": True, "user": dict(user)})

@app.route("/api/users", methods=["GET"])
def get_users():
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id,name,email,joined FROM users ORDER BY id DESC")
        users = [dict(r) for r in cur.fetchall()]
    return jsonify({"ok": True, "users": users})


# ════════════════════════════════════════════════════════
#  VIDEOS
# ════════════════════════════════════════════════════════
@app.route("/api/videos", methods=["GET"])
def get_videos():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM videos ORDER BY id DESC")
        videos = [dict(r) for r in cur.fetchall()]
    return jsonify({"ok": True, "videos": videos})

@app.route("/api/videos", methods=["POST", "OPTIONS"])
def add_video():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    d = request.json or {}
    if not d.get("title") or not d.get("link"):
        return jsonify({"ok": False, "error": "Title and link required"}), 400
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO videos (title,platform,link,thumb,desc,category,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *",
            (d.get("title"), d.get("platform","youtube"), d.get("link"),
             d.get("thumb",""), d.get("desc",""), d.get("category","general"), now())
        )
        video = dict(cur.fetchone())
    return jsonify({"ok": True, "video": video})

@app.route("/api/videos/<int:vid_id>", methods=["PUT", "OPTIONS"])
def update_video(vid_id):
    if request.method == "OPTIONS": return jsonify({}), 200
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    d = request.json or {}
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM videos WHERE id=%s", (vid_id,))
        existing = cur.fetchone()
        if not existing:
            return jsonify({"ok": False, "error": "Video not found"}), 404
        existing = dict(existing)
        cur.execute(
            "UPDATE videos SET title=%s,platform=%s,link=%s,thumb=%s,desc=%s,category=%s WHERE id=%s",
            (d.get("title", existing["title"]),
             d.get("platform", existing["platform"]),
             d.get("link", existing["link"]),
             d.get("thumb", existing["thumb"]),
             d.get("desc", existing["desc"]),
             d.get("category", existing["category"]),
             vid_id)
        )
    return jsonify({"ok": True})

@app.route("/api/videos/<int:vid_id>", methods=["DELETE", "OPTIONS"])
def delete_video(vid_id):
    if request.method == "OPTIONS": return jsonify({}), 200
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM videos WHERE id=%s", (vid_id,))
        cur.execute("DELETE FROM vreviews WHERE video_id=%s", (str(vid_id),))
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════════
#  VIDEO REVIEWS
# ════════════════════════════════════════════════════════
@app.route("/api/videos/<vid_id>/reviews", methods=["GET"])
def get_video_reviews(vid_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM vreviews WHERE video_id=%s ORDER BY id DESC", (str(vid_id),))
        revs = [dict(r) for r in cur.fetchall()]
    return jsonify({"ok": True, "reviews": revs})

@app.route("/api/videos/<vid_id>/reviews", methods=["POST", "OPTIONS"])
def add_video_review(vid_id):
    if request.method == "OPTIONS": return jsonify({}), 200
    d = request.json or {}
    if not d.get("user_id") or not d.get("stars") or not d.get("text"):
        return jsonify({"ok": False, "error": "Missing fields"}), 400
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM vreviews WHERE video_id=%s AND user_id=%s",
            (str(vid_id), str(d["user_id"]))
        )
        if cur.fetchone():
            return jsonify({"ok": False, "error": "Already reviewed"}), 409
        cur.execute(
            "INSERT INTO vreviews (video_id,user_id,author,stars,text,time) VALUES (%s,%s,%s,%s,%s,%s) RETURNING *",
            (str(vid_id), str(d["user_id"]), d.get("author","Anonymous"),
             d["stars"], d["text"], now())
        )
        review = dict(cur.fetchone())
    return jsonify({"ok": True, "review": review})


# ════════════════════════════════════════════════════════
#  MESSAGES
# ════════════════════════════════════════════════════════
@app.route("/api/messages", methods=["GET"])
def get_messages():
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages ORDER BY id DESC")
        msgs = [dict(r) for r in cur.fetchall()]
    return jsonify({"ok": True, "messages": msgs})

@app.route("/api/messages", methods=["POST", "OPTIONS"])
def add_message():
    if request.method == "OPTIONS": return jsonify({}), 200
    d = request.json or {}
    if not d.get("name") or not d.get("email") or not d.get("message"):
        return jsonify({"ok": False, "error": "Required fields missing"}), 400
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (name,email,phone,service,message,time,read) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (d.get("name"), d.get("email"), d.get("phone",""),
             d.get("service",""), d.get("message"), now(), "false")
        )
    return jsonify({"ok": True})

@app.route("/api/messages/<int:msg_id>/read", methods=["PUT", "OPTIONS"])
def mark_read(msg_id):
    if request.method == "OPTIONS": return jsonify({}), 200
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE messages SET read='true' WHERE id=%s", (msg_id,))
    return jsonify({"ok": True})

@app.route("/api/messages/<int:msg_id>", methods=["DELETE", "OPTIONS"])
def delete_message(msg_id):
    if request.method == "OPTIONS": return jsonify({}), 200
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE id=%s", (msg_id,))
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════════
#  STUDIO REVIEWS
# ════════════════════════════════════════════════════════
@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM reviews ORDER BY id DESC")
        revs = [dict(r) for r in cur.fetchall()]
    return jsonify({"ok": True, "reviews": revs})

@app.route("/api/reviews", methods=["POST", "OPTIONS"])
def add_review():
    if request.method == "OPTIONS": return jsonify({}), 200
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    d = request.json or {}
    if not d.get("author") or not d.get("text"):
        return jsonify({"ok": False, "error": "Author and text required"}), 400
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reviews (author,role,stars,text,visible,created_at) VALUES (%s,%s,%s,%s,%s,%s) RETURNING *",
            (d.get("author"), d.get("role",""), d.get("stars","5"),
             d.get("text"), "true", now())
        )
        review = dict(cur.fetchone())
    return jsonify({"ok": True, "review": review})

@app.route("/api/reviews/<int:rev_id>/toggle", methods=["PUT", "OPTIONS"])
def toggle_review(rev_id):
    if request.method == "OPTIONS": return jsonify({}), 200
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT visible FROM reviews WHERE id=%s", (rev_id,))
        r = cur.fetchone()
        if not r: return jsonify({"ok": False, "error": "Not found"}), 404
        new_val = "false" if r["visible"] == "true" else "true"
        cur.execute("UPDATE reviews SET visible=%s WHERE id=%s", (new_val, rev_id))
    return jsonify({"ok": True})

@app.route("/api/reviews/<int:rev_id>", methods=["DELETE", "OPTIONS"])
def delete_review(rev_id):
    if request.method == "OPTIONS": return jsonify({}), 200
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM reviews WHERE id=%s", (rev_id,))
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════════
#  STATS
# ════════════════════════════════════════════════════════
@app.route("/api/stats", methods=["GET"])
def get_stats():
    if not check_admin(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM videos");    videos   = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM messages");  messages = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM messages WHERE read='false'"); unread = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM users");     users    = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM reviews");   reviews  = cur.fetchone()["c"]
    return jsonify({"ok": True, "videos": videos, "messages": messages,
                    "unread": unread, "users": users, "reviews": reviews})


# ─── STARTUP ──────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("\n" + "="*50)
    print("  VK SON — Backend Server Running")
    print("  URL : http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)