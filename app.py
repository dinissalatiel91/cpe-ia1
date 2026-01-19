"""
app.py
------
Aplicação Flask completa.

Funcionalidades:
- Registo/Login/Logout (WTForms + Flask-Login + Werkzeug)
- Chat (pergunta -> similaridade -> resposta)
- Sugestões
- Histórico do utilizador
- Alterar palavra-passe (mostra nova password no ecrã)
- Área Admin: CRUD de Perguntas/Respostas (QA)

Notas para defesa:
- Sem LLM: matching por similaridade (TF-IDF leve)
- spaCy para normalização em Português
- SQLite embutido para portabilidade (instance/app.db)
"""

import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, QAItem, ChatMessage
from forms import RegisterForm, LoginForm, ChatForm, ChangePasswordForm, QAForm
from nlp_utils import match_question


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # Chave para CSRF + sessão (fixa, para não quebrar sessão/CSRF)
    app.config["SECRET_KEY"] = "cpe_ia_secret_key_2026_fix"

    # ✅ Caminho ABSOLUTO para a BD dentro do instance/
    # Isto elimina 100% dos problemas do seed criar num sítio e o app ler noutro.
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()

    # -------------------------
    # Rotas públicas
    # -------------------------
    @app.route("/")
    def landing():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        return render_template("landing.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            email = form.email.data.lower().strip()

            if User.query.filter_by(email=email).first():
                flash("Este email já está registado.", "warning")
                return redirect(url_for("register"))

            user = User(
                full_name=form.full_name.data.strip(),
                email=email,
                password_hash=generate_password_hash(form.password.data),
                is_admin=False,
            )
            db.session.add(user)
            db.session.commit()

            flash("Conta criada com sucesso. Agora entra.", "success")
            return redirect(url_for("login"))

        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            email = form.email.data.lower().strip()
            user = User.query.filter_by(email=email).first()

            if not user or not check_password_hash(user.password_hash, form.password.data):
                flash("Credenciais inválidas.", "danger")
                return redirect(url_for("login"))

            login_user(user, remember=form.remember.data)
            return redirect(url_for("index"))

        # Se validate_on_submit falhar, vamos continuar a mostrar a página
        # e o template vai exibir erros do WTForms.
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Sessão terminada.", "info")
        return redirect(url_for("login"))

    # -------------------------
    # Chat / Histórico / Conta
    # -------------------------
    @app.route("/chat", methods=["GET", "POST"])
    @login_required
    def index():
        form = ChatForm()

        messages = (
            ChatMessage.query
            .filter_by(user_id=current_user.id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        qa_items = QAItem.query.order_by(QAItem.id.desc()).limit(8).all()
        suggestion_questions = [q.question for q in qa_items]

        if form.validate_on_submit():
            user_q = form.question.data.strip()

            db.session.add(ChatMessage(user_id=current_user.id, role="user", content=user_q))
            db.session.commit()

            all_qa = QAItem.query.all()
            stored_questions = [x.question for x in all_qa]

            if not all_qa:
                answer = (
                    "Ainda não tenho base de conhecimento carregada. "
                    "Pede ao admin para adicionar Perguntas/Respostas."
                )
            else:
                ranked = match_question(user_q, stored_questions, top_k=3)
                best_idx, best_score = ranked[0]

                if best_score < 0.12:
                    answer = (
                        "Não encontrei uma correspondência forte para isso. "
                        "Tenta reformular a pergunta (mais concreta) ou escolhe uma sugestão."
                    )
                else:
                    answer = all_qa[best_idx].answer

            db.session.add(ChatMessage(user_id=current_user.id, role="assistant", content=answer))
            db.session.commit()

            return redirect(url_for("index"))

        return render_template(
            "index.html",
            form=form,
            messages=messages,
            suggestions=suggestion_questions
        )

    @app.route("/history")
    @login_required
    def history():
        messages = (
            ChatMessage.query
            .filter_by(user_id=current_user.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(200)
            .all()
        )
        return render_template("history.html", messages=messages)

    @app.route("/change-password", methods=["GET", "POST"])
    @login_required
    def change_password():
        form = ChangePasswordForm()
        shown_new_password = None

        if form.validate_on_submit():
            if not check_password_hash(current_user.password_hash, form.current_password.data):
                flash("A palavra-passe actual está errada.", "danger")
                return redirect(url_for("change_password"))

            new_pw = form.new_password.data
            current_user.password_hash = generate_password_hash(new_pw)
            db.session.commit()

            shown_new_password = new_pw
            flash("Palavra-passe actualizada.", "success")

        return render_template("change_password.html", form=form, shown_new_password=shown_new_password)

    # -------------------------
    # Admin (CRUD QA)
    # -------------------------
    def admin_required() -> bool:
        if not current_user.is_admin:
            flash("Acesso restrito (Admin).", "warning")
            return False
        return True

    @app.route("/admin/qa", methods=["GET", "POST"])
    @login_required
    def admin_qa():
        if not admin_required():
            return redirect(url_for("index"))

        form = QAForm()

        if form.validate_on_submit():
            qa = QAItem(question=form.question.data.strip(), answer=form.answer.data.strip())
            db.session.add(qa)
            db.session.commit()
            flash("Pergunta/Resposta adicionada.", "success")
            return redirect(url_for("admin_qa"))

        items = QAItem.query.order_by(QAItem.updated_at.desc()).all()
        return render_template("admin_qa.html", form=form, items=items)

    @app.route("/admin/qa/<int:qa_id>/delete", methods=["POST"])
    @login_required
    def admin_qa_delete(qa_id: int):
        if not admin_required():
            return redirect(url_for("index"))

        qa = QAItem.query.get_or_404(qa_id)
        db.session.delete(qa)
        db.session.commit()
        flash("Item eliminado.", "info")
        return redirect(url_for("admin_qa"))

    @app.route("/admin/qa/<int:qa_id>/edit", methods=["GET", "POST"])
    @login_required
    def admin_qa_edit(qa_id: int):
        if not admin_required():
            return redirect(url_for("index"))

        qa = QAItem.query.get_or_404(qa_id)
        form = QAForm(obj=qa)

        if form.validate_on_submit():
            qa.question = form.question.data.strip()
            qa.answer = form.answer.data.strip()
            db.session.commit()
            flash("Item actualizado.", "success")
            return redirect(url_for("admin_qa"))

        return render_template(
            "admin_qa.html",
            form=form,
            items=QAItem.query.order_by(QAItem.updated_at.desc()).all(),
            editing_id=qa_id
        )

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
