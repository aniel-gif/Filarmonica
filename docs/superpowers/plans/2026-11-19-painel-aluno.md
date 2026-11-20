# Painel do Aluno Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a dedicated student dashboard and profile system where students can log in with their existing account, view their active instrument loans, return dates, and scheduled events for the philharmonic.

**Architecture:** 
1. Update `Usuario` and `Aluno` models or linking mechanism so that an `Aluno` can be associated with a `Usuario` (or login directly as an `Aluno`).
2. Add role differentiation or direct student role check (`is_aluno` or `aluno_id` in session) so students are automatically redirected to `/aluno/dashboard`.
3. Create the student dashboard route and HTML template displaying loans, return deadlines, and upcoming events.

**Tech Stack:** Flask, SQLAlchemy, Flask-WTF, Bootstrap 5 (existing UI styling).

**Spec:** Desenhado interativamente com o usuário (perfil e painel do aluno).

## Global Constraints
- Database compatibility: PostgreSQL on Neon (production) and SQLite (development).
- Maintain existing authentication structure (Flask session).

## Review Focus
- **Security / IDOR:** Ensure students can only view their own loans and data, never other students' information.
- **Role Routing:** Ensure students logging in are correctly directed to the student dashboard, while admins go to the main admin dashboard.

---

### Task 1: Update Models and Migration/Database schema

**Files:**
- Modify: `models.py`
- Test: `test_aluno_model.py` (temporary test or inline script)

**Interfaces:**
- Consumes: `Usuario`, `Aluno`
- Produces: Relationship or foreign key linking `Aluno` to `Usuario`.

- [ ] **Step 1: Update `Aluno` model in `models.py` to optionally link to `Usuario`**
```python
# In models.py, add usuario_id to Aluno model:
usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
usuario = db.relationship('Usuario', backref='aluno_perfil', lazy=True)
```

- [ ] **Step 2: Create migration/update script for database (Neon & SQLite)**
Write a quick check in `app.py` or run a script to add `usuario_id` to `alunos` table if missing.

- [ ] **Step 3: Commit**
```bash
git add models.py app.py
git commit -m "feat: link Aluno model to Usuario for student profiles"
```

---

### Task 2: Student Login Routing & Access Control

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `Usuario`, `Aluno`
- Produces: `/aluno/dashboard` route and conditional login redirect.

- [ ] **Step 1: Update login route in `app.py` to check if user is an associated student**
```python
# In login route:
user = Usuario.query.filter_by(email=form.email.data).first()
if user and check_password_hash(user.senha_hash, form.senha.data):
    session['usuario_id'] = user.id
    session['usuario_nome'] = user.nome
    
    # Check if this user is linked to an Aluno
    aluno_perfil = Aluno.query.filter_by(usuario_id=user.id).first()
    if aluno_perfil:
        session['aluno_id'] = aluno_perfil.id
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('aluno_dashboard'))
    else:
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
```

- [ ] **Step 2: Implement `/aluno/dashboard` route**
```python
@app.route('/aluno/dashboard')
def aluno_dashboard():
    if 'usuario_id' not in session or 'aluno_id' not in session:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))
    
    aluno = Aluno.query.get_or_404(session['aluno_id'])
    emprestimos = Emprestimo.query.filter_by(aluno_id=aluno.id).all()
    eventos = Evento.query.order_by(Evento.data.asc()).all()
    
    return render_template('aluno_dashboard.html', aluno=aluno, emprestimos=emprestimos, eventos=eventos)
```

- [ ] **Step 3: Commit**
```bash
git add app.py
git commit -m "feat: add student dashboard route and login redirection"
```

---

### Task 3: Create Student Dashboard Template

**Files:**
- Create: `templates/aluno_dashboard.html`

**Interfaces:**
- Consumes: `aluno`, `emprestimos`, `eventos`
- Produces: Responsive HTML page for student view.

- [ ] **Step 1: Create `templates/aluno_dashboard.html` with sections for loans, return dates, and events**
Follow existing Bootstrap 5 templates style used in `dashboard.html`.

- [ ] **Step 2: Commit**
```bash
git add templates/aluno_dashboard.html
git commit -m "feat: add student dashboard HTML template"
```

---

### Task 4: Verification and Deployment

**Files:**
- Modify: `app.py` (if needed for final adjustments)

- [ ] **Step 1: Verify all routes and database schema locally/remotely**
- [ ] **Step 2: Push changes to GitHub and verify Render deploy**
```bash
git push origin main
```
