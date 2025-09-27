from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
import json

app = Flask(__name__)
app.secret_key = "supersecret588"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Models
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    facebook_link = db.Column(db.String(500), nullable=True)

class Button(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    path = db.Column(db.String(500))

class Config(db.Model):
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(1000))

# Admin code
ADMIN_CODE = "UF-588-JAYWNYY"

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# Routes
@app.route("/")
def home():
    # pass total member count
    total = Member.query.count()
    return render_template("home.html", total_members=total)

@app.route("/sabudbob")
def sabudbob():
    members = Member.query.all()
    members_list = [{"id":m.id, "name":m.name, "link":m.facebook_link or ""} for m in members]
    return render_template("sabudbob.html", members=members_list)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        code = request.form.get("password") or request.form.get("code") or ""
        if code == ADMIN_CODE:
            session["admin_logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("รหัสไม่ถูกต้อง", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    total_members = Member.query.count()
    total_buttons = Button.query.count()
    return render_template("dashboard.html", total_members=total_members, total_buttons=total_buttons)

# Members management (admin)
@app.route("/members", methods=["GET","POST"])
@login_required
def members_page():
    if request.method == "POST":
        name = request.form.get("name")
        facebook = request.form.get("facebook")
        if name:
            m = Member(name=name, facebook_link=facebook)
            db.session.add(m)
            db.session.commit()
            flash("เพิ่มสมาชิกเรียบร้อย", "success")
        return redirect(url_for("members_page"))
    members = Member.query.order_by(Member.id).all()
    return render_template("members.html", members=members)

@app.route("/delete_member/<int:id>", methods=["POST"])
@login_required
def delete_member(id):
    m = Member.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    flash("ลบสมาชิกแล้ว", "success")
    return redirect(url_for("members_page"))

# Buttons management (admin)
@app.route("/buttons", methods=["GET","POST"])
@login_required
def buttons_page():
    if request.method == "POST":
        title = request.form.get("title")
        path = request.form.get("path")
        if title:
            b = Button(title=title, path=path)
            db.session.add(b)
            db.session.commit()
            flash("เพิ่มปุ่มเรียบร้อย", "success")
        return redirect(url_for("buttons_page"))
    buttons = Button.query.all()
    return render_template("buttons.html", buttons=[{"id":b.id,"title":b.title,"path":b.path} for b in buttons])

@app.route("/delete_button/<int:id>", methods=["POST"])
@login_required
def delete_button(id):
    b = Button.query.get_or_404(id)
    db.session.delete(b)
    db.session.commit()
    flash("ลบปุ่มแล้ว", "success")
    return redirect(url_for("buttons_page"))

# Configuration (admin)
@app.route("/configuration", methods=["GET","POST"])
@login_required
def configuration():
    if request.method == "POST":
        for k in ["brand_symbol","brand_name","badge_text","main_title","subtitle"]:
            v = request.form.get(k,"")
            cfg = Config.query.get(k)
            if cfg:
                cfg.value = v
            else:
                cfg = Config(key=k, value=v)
                db.session.add(cfg)
        db.session.commit()
        flash("บันทึกการตั้งค่าแล้ว", "success")
        return redirect(url_for("configuration"))
    cfg_items = {c.key: c.value for c in Config.query.all()}
    return render_template("configuration.html", cfg=cfg_items)

# API to get members count (used by home JS)
@app.route("/api/member_count")
def api_member_count():
    return {"count": Member.query.count()}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
