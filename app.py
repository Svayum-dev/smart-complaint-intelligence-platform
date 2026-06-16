from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from database import (
    init_db, get_stats, get_recent_complaints, get_all_complaints,
    get_analytics_data, add_complaint, update_status,
    get_complaint_by_id, store_ai_analysis,
)
from ai_analysis import analyze_complaint
from functools import wraps

app = Flask(__name__)
app.secret_key = 'scip-secret-2024-xk92'

# Security Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login', next=request.url))
        if session.get('role') != 'admin':
            flash('Access denied. Admin permissions required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


CATEGORIES = ['Roads & Infrastructure', 'Water Supply', 'Electricity', 'Sanitation', 'Public Safety', 'Noise Pollution', 'Parks & Recreation', 'Drainage']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
STATUSES = ['Open', 'In Progress', 'Resolved']


@app.route('/')
@login_required
def dashboard():
    user_id = None if session.get('role') == 'admin' else session.get('user_id')
    stats = get_stats(user_id=user_id)
    recent = get_recent_complaints(10, user_id=user_id)
    return render_template('dashboard.html', stats=stats, recent=recent)


@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        category    = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        priority    = request.form.get('priority', '').strip()
        location    = request.form.get('location', '').strip()

        errors = []
        if not title:
            errors.append('Title is required.')
        if category not in CATEGORIES:
            errors.append('Please select a valid category.')
        if priority not in PRIORITIES:
            errors.append('Please select a valid priority.')

        if errors:
            return render_template('submit.html', categories=CATEGORIES, priorities=PRIORITIES,
                                   errors=errors, form_data=request.form)

        # 1️⃣ Save complaint — get back the new id
        complaint_id = add_complaint(title, category, description, priority, location, user_id=session.get('user_id'))

        # 2️⃣ Run Gemini analysis synchronously (gemini-2.0-flash is fast ~1-2s)
        ai = analyze_complaint(title, description, location)
        if ai:
            store_ai_analysis(
                complaint_id,
                ai['category'],
                ai['priority'],
                ai['department'],
                ai['summary'],
            )

        flash('Complaint submitted successfully! AI analysis complete.', 'success')
        return redirect(url_for('complaint_detail', complaint_id=complaint_id))

    return render_template('submit.html', categories=CATEGORIES, priorities=PRIORITIES,
                           errors=[], form_data={})


@app.route('/complaint/<int:complaint_id>')
@login_required
def complaint_detail(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if complaint is None:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('history'))
        
    # Resident can only view their own complaints
    if session.get('role') != 'admin' and complaint['user_id'] != session.get('user_id'):
        flash('Access denied. You do not have permission to view this complaint.', 'danger')
        return redirect(url_for('dashboard'))
        
    return render_template('complaint_detail.html', complaint=complaint, statuses=STATUSES)


@app.route('/history')
@login_required
def history():
    page     = int(request.args.get('page', 1))
    category = request.args.get('category', '')
    priority = request.args.get('priority', '')
    status   = request.args.get('status', '')
    sort     = request.args.get('sort', 'created_at')
    order    = request.args.get('order', 'desc')

    user_id = None if session.get('role') == 'admin' else session.get('user_id')
    complaints, total, total_pages = get_all_complaints(
        page=page, per_page=12,
        category=category or None,
        priority=priority or None,
        status=status or None,
        sort=sort, order=order,
        user_id=user_id
    )

    return render_template('history.html',
                           complaints=complaints,
                           total=total,
                           total_pages=total_pages,
                           page=page,
                           category=category,
                           priority=priority,
                           status=status,
                           sort=sort,
                           order=order,
                           categories=CATEGORIES,
                           priorities=PRIORITIES,
                           statuses=STATUSES)


@app.route('/analytics')
@admin_required
def analytics():
    return render_template('analytics.html')


@app.route('/api/analytics')
@admin_required
def api_analytics():
    months = request.args.get('range', 6, type=int)
    data = get_analytics_data(months=months)
    return jsonify(data)


@app.route('/api/update-status', methods=['POST'])
@admin_required
def api_update_status():
    data       = request.get_json()
    complaint_id = data.get('id')
    new_status = data.get('status')
    if new_status not in STATUSES:
        return jsonify({'error': 'Invalid status'}), 400
    update_status(complaint_id, new_status)
    return jsonify({'success': True, 'status': new_status})


@app.route('/api/complaint/<int:complaint_id>/analyze', methods=['POST'])
@admin_required
def api_analyze_complaint(complaint_id):
    complaint = get_complaint_by_id(complaint_id)
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404
    
    import os
    if not os.environ.get('GEMINI_API_KEY'):
        return jsonify({
            'error': 'Gemini API Key is not configured on the server. Please set the GEMINI_API_KEY environment variable.'
        }), 400
    
    ai = analyze_complaint(complaint['title'], complaint['description'] or '', complaint['location'] or '')
    if ai:
        store_ai_analysis(
            complaint_id,
            ai['category'],
            ai['priority'],
            ai['department'],
            ai['summary']
        )
        return jsonify({
            'success': True,
            'ai_category': ai['category'],
            'ai_priority': ai['priority'],
            'ai_department': ai['department'],
            'ai_summary': ai['summary']
        })
    return jsonify({'error': 'AI analysis failed'}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    errors = []
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            errors.append('Please provide both username and password.')
        else:
            from database import get_user_by_username
            from werkzeug.security import check_password_hash
            user = get_user_by_username(username)
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                flash(f"Welcome back, {user['full_name']}!", 'success')
                next_url = request.args.get('next')
                return redirect(next_url or url_for('dashboard'))
            else:
                errors.append('Invalid username or password.')
                
    return render_template('login.html', errors=errors)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    errors = []
    form_data = {}
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        
        form_data = {'username': username, 'full_name': full_name}
        
        if not username or not password or not full_name:
            errors.append('All fields are required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        else:
            # Strong password criteria validation
            if len(password) < 8:
                errors.append('Password must be at least 8 characters long.')
            if not any(c.isupper() for c in password):
                errors.append('Password must contain at least one uppercase letter.')
            if not any(c.islower() for c in password):
                errors.append('Password must contain at least one lowercase letter.')
            if not any(c.isdigit() for c in password):
                errors.append('Password must contain at least one digit.')
            if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" for c in password):
                errors.append('Password must contain at least one special character (e.g., !, @, #, $, etc.).')

            if not errors:
                from database import create_user
                user_id = create_user(username, password, 'resident', full_name)
                if user_id:
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login'))
                else:
                    errors.append('Username is already taken.')

                
    return render_template('register.html', errors=errors, form_data=form_data)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    print("[OK] Smart Complaint Intelligence Platform running at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
