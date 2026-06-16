import sqlite3
import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'complaints.db')

CATEGORIES = ['Roads & Infrastructure', 'Water Supply', 'Electricity', 'Sanitation', 'Public Safety', 'Noise Pollution', 'Parks & Recreation', 'Drainage']
PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
STATUSES = ['Open', 'In Progress', 'Resolved']
LOCATIONS = [
    'Block A, Sector 12', 'Block B, Sector 5', 'Main Gate Area', 'Community Hall',
    'Park Area, Zone 3', 'Block C, Sector 9', 'Swimming Pool Complex', 'Block D, Sector 1',
    'Parking Lot B', 'Block E, Sector 7', 'Children\'s Play Area', 'Block F, Sector 14',
    'Society Office', 'Block G, Sector 3', 'Club House', 'Block H, Sector 11'
]

SEED_COMPLAINTS = [
    ('Pothole on Main Road', 'Roads & Infrastructure', 'Large pothole near the main entrance causing vehicle damage. Multiple residents have complained.', 'High', 'Open'),
    ('Street Light Not Working', 'Electricity', 'Three consecutive street lights on Block B road have been out for 2 weeks.', 'Medium', 'In Progress'),
    ('Water Supply Disruption', 'Water Supply', 'No water supply in Block C from 6 AM to 2 PM daily for the past week.', 'Critical', 'Open'),
    ('Overflowing Dustbin', 'Sanitation', 'Dustbin near Block A entrance overflowing and creating hygiene issues.', 'High', 'Resolved'),
    ('Stray Dogs Near Playground', 'Public Safety', 'Pack of stray dogs near children\'s playground creating safety concerns.', 'Critical', 'In Progress'),
    ('Loud Music Late Night', 'Noise Pollution', 'Loud music from Block D flat 302 every weekend past midnight.', 'Medium', 'Open'),
    ('Broken Swing in Park', 'Parks & Recreation', 'Main swing in children\'s play area is broken and poses injury risk.', 'High', 'Open'),
    ('Drainage Clog on Street', 'Drainage', 'Water clogging due to blocked drain near Block E. Health hazard in monsoon.', 'Critical', 'Resolved'),
    ('Unauthorized Parking', 'Roads & Infrastructure', 'Vehicles parked blocking the fire exit lane near Block B for weeks.', 'Medium', 'Resolved'),
    ('Electricity Fluctuation', 'Electricity', 'Frequent voltage fluctuations in Block A causing appliance damage.', 'High', 'In Progress'),
    ('Broken Water Pipe', 'Water Supply', 'Leaking underground pipe near parking lot causing water wastage.', 'High', 'Open'),
    ('Garbage Pickup Missed', 'Sanitation', 'Garbage not collected from Block G for 3 consecutive days.', 'Medium', 'Resolved'),
    ('CCTV Camera Down', 'Public Safety', 'CCTV camera at main gate has been non-functional for over a month.', 'High', 'In Progress'),
    ('Park Lighting Broken', 'Parks & Recreation', 'All lights in the evening walking park are out. Unsafe at night.', 'High', 'Open'),
    ('Sewage Overflow', 'Drainage', 'Sewage overflowing onto footpath near Block H. Urgent attention needed.', 'Critical', 'Open'),
    ('Road Speed Breaker Damaged', 'Roads & Infrastructure', 'Speed breaker on internal road broken and causing vehicle scraping.', 'Low', 'Resolved'),
    ('Power Outage', 'Electricity', 'Complete power outage in Zone C for 6+ hours with no communication from maintenance.', 'Critical', 'Resolved'),
    ('Muddy Water Supply', 'Water Supply', 'Brown/muddy water coming from taps in Block D. Possibly contaminated.', 'Critical', 'In Progress'),
    ('Illegal Construction Noise', 'Noise Pollution', 'Construction work happening beyond permitted hours at Block F.', 'High', 'Open'),
    ('Park Bench Damaged', 'Parks & Recreation', 'Multiple benches in main park have nails sticking out. Injury risk.', 'Medium', 'Open'),
    ('Waterlogging at Entrance', 'Drainage', 'Main entrance waterlogged after every rain. Very inconvenient.', 'High', 'Resolved'),
    ('Broken Society Gate', 'Public Safety', 'Society main gate hinge is broken and remains open unmonitored.', 'Critical', 'In Progress'),
    ('Transformer Humming Loud', 'Electricity', 'Transformer near Block C making loud humming noise disturbing sleep.', 'Low', 'Open'),
    ('Water Meter Faulty', 'Water Supply', 'Water meter at Block B showing incorrect readings for 2 months.', 'Medium', 'Open'),
    ('Dead Animal on Road', 'Sanitation', 'Dead animal carcass on internal road not cleared for 2 days.', 'High', 'Resolved'),
    ('Missing Manhole Cover', 'Drainage', 'Manhole cover missing near parking area — serious accident risk.', 'Critical', 'Open'),
    ('Burnt Street Light', 'Electricity', 'Street light near Block A has been sparking and then went dark.', 'High', 'In Progress'),
    ('Restricted Area Violation', 'Public Safety', 'Unauthorized persons accessing terrace area regularly at night.', 'High', 'Open'),
    ('Cracked Pavement', 'Roads & Infrastructure', 'Footpath tiles cracked and uneven near Block C. Tripping hazard for elderly.', 'Low', 'Open'),
    ('Gym Equipment Broken', 'Parks & Recreation', 'Treadmill and cycle machine in society gym out of order.', 'Medium', 'Resolved'),
    ('Mosquito Breeding Near Pool', 'Sanitation', 'Stagnant water near swimming pool creating mosquito breeding ground.', 'High', 'In Progress'),
    ('Dog Fouling in Park', 'Sanitation', 'Dog owners not cleaning up after their pets in the main park.', 'Low', 'Open'),
    ('Elevator Not Working', 'Electricity', 'Elevator in Block B tower has been non-functional for 3 days.', 'High', 'Open'),
    ('Fire Hydrant Leaking', 'Water Supply', 'Fire hydrant near Block A leaking continuously. Water wastage.', 'Medium', 'In Progress'),
    ('Children Cycling on Roads', 'Public Safety', 'No speed reducers or signs to protect children cycling in internal lanes.', 'Low', 'Open'),
    ('Wall Crack Near Entrance', 'Roads & Infrastructure', 'Crack observed on compound wall near east entrance gate.', 'High', 'Open'),
    ('Mobile Tower Noise', 'Noise Pollution', 'Mobile tower cooling unit on Block H terrace very noisy at night.', 'Medium', 'In Progress'),
    ('Swimming Pool Dirty', 'Parks & Recreation', 'Swimming pool water appears green and hasn\'t been cleaned in weeks.', 'High', 'Open'),
    ('Meter Room Unsecured', 'Electricity', 'Electricity meter room in Block D left unlocked and accessible to anyone.', 'Medium', 'Open'),
    ('Water Tank Overflow', 'Water Supply', 'Overhead water tank overflowing daily, wasting water and wetting terrace.', 'Medium', 'Resolved'),
    ('Tree Branch Fallen', 'Parks & Recreation', 'Large tree branch fell on the footpath. Blocking pedestrian movement.', 'High', 'Resolved'),
    ('Night Guard Absent', 'Public Safety', 'Night security guard often absent between 2 AM to 4 AM.', 'Critical', 'In Progress'),
    ('Paint Peeling at Lobby', 'Roads & Infrastructure', 'Paint peeling and damp patches appearing in Block C lobby.', 'Low', 'Open'),
    ('Intercom Not Working', 'Electricity', 'Intercom system in Block E not functioning. Communication problem.', 'Medium', 'Open'),
    ('Waterlogging in Basement', 'Drainage', 'Basement parking flooded during last rain. Several cars damaged.', 'Critical', 'Open'),
    ('Foul Smell from Drain', 'Sanitation', 'Terrible smell coming from drain near Block F. Unbearable in summer.', 'High', 'In Progress'),
    ('Gate Intercom Broken', 'Public Safety', 'Visitor intercom at main gate completely non-functional.', 'High', 'Open'),
    ('Missing Signboards', 'Roads & Infrastructure', 'Speed limit and directional signs missing inside society roads.', 'Low', 'Resolved'),
    ('Terrace Waterproofing Damage', 'Drainage', 'Terrace waterproofing on Block A damaged, causing seepage in top floor flats.', 'High', 'Open'),
    ('Railing Loose on Staircase', 'Public Safety', 'Staircase railing on Block D loose and wobbling. Injury risk for elderly.', 'Critical', 'Open'),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and seed with realistic data if empty."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL,
            full_name     TEXT NOT NULL,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT NOT NULL,
            category      TEXT NOT NULL,
            description   TEXT,
            priority      TEXT NOT NULL,
            status        TEXT DEFAULT 'Open',
            location      TEXT,
            user_id       INTEGER,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            ai_category   TEXT,
            ai_priority   TEXT,
            ai_department TEXT,
            ai_summary    TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Safe migration: add AI and User columns to existing databases
    existing_cols = {row[1] for row in cursor.execute('PRAGMA table_info(complaints)').fetchall()}
    ai_columns = {
        'ai_category':   'TEXT',
        'ai_priority':   'TEXT',
        'ai_department': 'TEXT',
        'ai_summary':    'TEXT',
        'user_id':       'INTEGER'
    }
    for col, col_type in ai_columns.items():
        if col not in existing_cols:
            cursor.execute(f'ALTER TABLE complaints ADD COLUMN {col} {col_type}')
            print(f'[DB] Migrated: added column {col}')
    conn.commit()

    # Seed default users if users table is empty
    cursor.execute('SELECT COUNT(*) as cnt FROM users')
    user_count = cursor.fetchone()['cnt']
    if user_count == 0:
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        ''', ('admin', generate_password_hash('admin123'), 'admin', 'Admin Manager'))
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        ''', ('resident', generate_password_hash('resident123'), 'resident', 'Jane Resident'))
        conn.commit()
        print("[OK] Seeded default admin and resident users.")

    # Get the default resident user ID for seeding/assigning complaints
    cursor.execute("SELECT id FROM users WHERE username = 'resident'")
    resident_row = cursor.fetchone()
    resident_id = resident_row['id'] if resident_row else 1

    # Update any existing complaints with user_id NULL to the default resident_id
    cursor.execute("UPDATE complaints SET user_id = ? WHERE user_id IS NULL", (resident_id,))
    conn.commit()

    cursor.execute('SELECT COUNT(*) as cnt FROM complaints')
    count = cursor.fetchone()['cnt']

    if count == 0:
        now = datetime.now()
        rows = []
        for i, (title, category, description, priority, status) in enumerate(SEED_COMPLAINTS):
            days_ago = random.randint(0, 180)
            created = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            updated = created + timedelta(hours=random.randint(1, 72))
            location = random.choice(LOCATIONS)
            rows.append((title, category, description, priority, status, location, resident_id,
                         created.strftime('%Y-%m-%d %H:%M:%S'),
                         updated.strftime('%Y-%m-%d %H:%M:%S')))

        cursor.executemany('''
            INSERT INTO complaints (title, category, description, priority, status, location, user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)
        conn.commit()
        print(f"[OK] Seeded {len(rows)} complaints into database.")

    conn.close()



def get_stats(user_id=None):
    conn = get_db()
    c = conn.cursor()
    stats = {}
    if user_id is not None:
        stats['total'] = c.execute('SELECT COUNT(*) FROM complaints WHERE user_id = ?', (user_id,)).fetchone()[0]
        stats['open'] = c.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Open' AND user_id = ?", (user_id,)).fetchone()[0]
        stats['in_progress'] = c.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress' AND user_id = ?", (user_id,)).fetchone()[0]
        stats['resolved'] = c.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved' AND user_id = ?", (user_id,)).fetchone()[0]
        stats['high_priority'] = c.execute("SELECT COUNT(*) FROM complaints WHERE priority IN ('High', 'Critical') AND user_id = ?", (user_id,)).fetchone()[0]
    else:
        stats['total'] = c.execute('SELECT COUNT(*) FROM complaints').fetchone()[0]
        stats['open'] = c.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Open'").fetchone()[0]
        stats['in_progress'] = c.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'").fetchone()[0]
        stats['resolved'] = c.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'").fetchone()[0]
        stats['high_priority'] = c.execute("SELECT COUNT(*) FROM complaints WHERE priority IN ('High', 'Critical')").fetchone()[0]
    conn.close()
    return stats
def get_recent_complaints(limit=10, user_id=None):
    conn = get_db()
    if user_id is not None:
        rows = conn.execute(
            '''SELECT c.*, u.full_name AS raised_by, u.username AS raised_by_username 
               FROM complaints c 
               LEFT JOIN users u ON c.user_id = u.id 
               WHERE c.user_id = ? 
               ORDER BY c.created_at DESC LIMIT ?''', (user_id, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            '''SELECT c.*, u.full_name AS raised_by, u.username AS raised_by_username 
               FROM complaints c 
               LEFT JOIN users u ON c.user_id = u.id 
               ORDER BY c.created_at DESC LIMIT ?''', (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_complaints(page=1, per_page=12, category=None, priority=None, status=None, sort='created_at', order='desc', user_id=None):
    conn = get_db()
    where_clauses = []
    params = []
    if category:
        where_clauses.append('c.category = ?')
        params.append(category)
    if priority:
        where_clauses.append('c.priority = ?')
        params.append(priority)
    if status:
        where_clauses.append('c.status = ?')
        params.append(status)
    if user_id is not None:
        where_clauses.append('c.user_id = ?')
        params.append(user_id)

    where_sql = ('WHERE ' + ' AND '.join(where_clauses)) if where_clauses else ''
    
    # Map sort columns safely
    allowed_sorts = {
        'created_at': 'c.created_at',
        'title': 'c.title',
        'priority': 'c.priority',
        'status': 'c.status',
        'category': 'c.category',
        'id': 'c.id'
    }
    sort_col = allowed_sorts.get(sort, 'c.created_at')
    order = 'ASC' if order == 'asc' else 'DESC'

    total = conn.execute(f'SELECT COUNT(*) FROM complaints c {where_sql}', params).fetchone()[0]
    offset = (page - 1) * per_page
    rows = conn.execute(
        f'''SELECT c.*, u.full_name AS raised_by, u.username AS raised_by_username 
           FROM complaints c 
           LEFT JOIN users u ON c.user_id = u.id 
           {where_sql} 
           ORDER BY {sort_col} {order} LIMIT ? OFFSET ?''',
        params + [per_page, offset]
    ).fetchall()
    conn.close()
    total_pages = (total + per_page - 1) // per_page
    return [dict(r) for r in rows], total, total_pages



def get_analytics_data(months=6):
    """Return analytics data for the given time range. months=0 means all time."""
    conn = get_db()

    # Build reusable date clauses
    if months and months > 0:
        date_filter  = f"created_at >= date('now', '-{months} months')"
        where_clause = f"WHERE {date_filter}"
        and_clause   = f"AND {date_filter}"
    else:
        date_filter  = None
        where_clause = ""
        and_clause   = ""

    # ── Standard breakdowns ─────────────────────────────────────────
    by_category = conn.execute(f'''
        SELECT category, COUNT(*) as count FROM complaints
        {where_clause} GROUP BY category ORDER BY count DESC
    ''').fetchall()

    by_status = conn.execute(f'''
        SELECT status, COUNT(*) as count FROM complaints
        {where_clause} GROUP BY status
    ''').fetchall()

    by_priority = conn.execute(f'''
        SELECT priority, COUNT(*) as count FROM complaints
        {where_clause} GROUP BY priority
    ''').fetchall()

    monthly_trend = conn.execute(f'''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
        FROM complaints {where_clause}
        GROUP BY month ORDER BY month ASC
    ''').fetchall()

    # ── Resolution over time (monthly total vs resolved) ────────────
    resolution_ot = conn.execute(f'''
        SELECT
            strftime('%Y-%m', created_at)                            AS month,
            COUNT(*)                                                 AS total,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END)    AS resolved
        FROM complaints {where_clause}
        GROUP BY month ORDER BY month ASC
    ''').fetchall()

    # ── Category × Priority matrix ──────────────────────────────────
    cat_pri_rows = conn.execute(f'''
        SELECT category, priority, COUNT(*) as count
        FROM complaints {where_clause}
        GROUP BY category, priority
    ''').fetchall()

    cats_ordered = [r['category'] for r in by_category]
    matrix_map   = {}
    for row in cat_pri_rows:
        cat = row['category']; pri = row['priority']
        if cat not in matrix_map:
            matrix_map[cat] = {}
        matrix_map[cat][pri] = row['count']

    category_priority_matrix = []
    for cat in cats_ordered:
        entry = {'category': cat}
        for pri in ('Low', 'Medium', 'High', 'Critical'):
            entry[pri] = matrix_map.get(cat, {}).get(pri, 0)
        category_priority_matrix.append(entry)

    # ── KPI stats ───────────────────────────────────────────────────
    total         = conn.execute(f'SELECT COUNT(*) FROM complaints {where_clause}').fetchone()[0]
    resolved_cnt  = conn.execute(f"SELECT COUNT(*) FROM complaints WHERE status='Resolved' {and_clause}").fetchone()[0]
    critical_open = conn.execute(f"SELECT COUNT(*) FROM complaints WHERE priority='Critical' AND status!='Resolved' {and_clause}").fetchone()[0]
    this_month    = conn.execute(
        f"SELECT COUNT(*) FROM complaints WHERE strftime('%Y-%m', created_at)=strftime('%Y-%m','now') {and_clause}"
    ).fetchone()[0]
    avg_row = conn.execute(f'''
        SELECT AVG(CAST((julianday(updated_at) - julianday(created_at)) AS REAL)) AS avg_d
        FROM complaints WHERE status='Resolved' {and_clause}
    ''').fetchone()
    avg_days = round(avg_row[0] or 0, 1)

    conn.close()
    return {
        'by_category':              [dict(r) for r in by_category],
        'by_status':                [dict(r) for r in by_status],
        'by_priority':              [dict(r) for r in by_priority],
        'monthly_trend':            [dict(r) for r in monthly_trend],
        'resolution_over_time':     [dict(r) for r in resolution_ot],
        'category_priority_matrix': category_priority_matrix,
        'kpi': {
            'total':               total,
            'resolved':            resolved_cnt,
            'resolution_rate':     round((resolved_cnt / total * 100) if total else 0, 1),
            'critical_open':       critical_open,
            'this_month':          this_month,
            'avg_days_to_resolve': avg_days,
        },
    }


def add_complaint(title, category, description, priority, location, user_id=None):
    """Insert a new complaint and return its new id."""
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO complaints (title, category, description, priority, status, location, user_id)
        VALUES (?, ?, ?, ?, 'Open', ?, ?)
    ''', (title, category, description, priority, location, user_id))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_complaint_by_id(complaint_id):
    """Fetch a single complaint by id. Returns a dict or None."""
    conn = get_db()
    row = conn.execute(
        '''SELECT c.*, u.full_name AS raised_by, u.username AS raised_by_username 
           FROM complaints c 
           LEFT JOIN users u ON c.user_id = u.id 
           WHERE c.id = ?''', (complaint_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None



def store_ai_analysis(complaint_id, ai_category, ai_priority, ai_department, ai_summary):
    """Persist Gemini analysis results against an existing complaint."""
    conn = get_db()
    conn.execute('''
        UPDATE complaints
        SET ai_category = ?, ai_priority = ?, ai_department = ?, ai_summary = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (ai_category, ai_priority, ai_department, ai_summary, complaint_id))
    conn.commit()
    conn.close()


def update_status(complaint_id, new_status):
    conn = get_db()
    conn.execute('''
        UPDATE complaints SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (new_status, complaint_id))
    conn.commit()
    conn.close()


def create_user(username, password, role, full_name):
    """Create a new user with hashed password."""
    conn = get_db()
    try:
        cursor = conn.execute('''
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username.strip().lower(), generate_password_hash(password), role, full_name.strip()))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        user_id = None  # Username already exists
    conn.close()
    return user_id


def get_user_by_username(username):
    """Retrieve user details by username."""
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM users WHERE LOWER(username) = ?', (username.strip().lower(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    """Retrieve user details by id."""
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

