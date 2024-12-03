from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from geopy.distance import geodesic
from functools import wraps
from datetime import datetime
import pytz

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'user_login'

jakarta_tz = pytz.timezone('Asia/Jakarta')

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    @property
    def is_admin(self):
        return True  # Admin adalah admin


class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_kelas = db.Column(db.String(5), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100),nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    classes_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    classes = db.relationship('Classes', backref='user')
    @property
    def is_admin(self):
        return False  # User biasa bukan admin
    

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(jakarta_tz))
    status = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)  # Kolom untuk menyimpan lokasi (latitude, longitude)
    attempts = db.Column(db.Integer, default=0)  # Kolom untuk menyimpan jumlah percobaan
    user = db.relationship('User', backref='attendances')  # Relasi ke model User


@login_manager.user_loader
def load_user(user_id):
    # Pertama coba cari di tabel User
    user = User.query.get(int(user_id))
    if user:
        return user
    # Jika tidak ditemukan di User, coba cari di tabel Admin
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    return None  # Jika tidak ada, kembalikan None

# Dekorator untuk akses berbasis role
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not isinstance(current_user, Admin):
            abort(403)  # Hanya admin yang dapat mengakses
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Memeriksa apakah pengguna adalah admin atau user berdasarkan model
            if role == 'admin' and not current_user.is_admin:
                abort(403)  # Forbidden, jika bukan admin
            elif role == 'user' and current_user.is_admin:
                abort(403)  # Forbidden, jika admin mencoba akses user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
@login_required
def home():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('dashboard'))


# Rute untuk login sebagai admin
@app.route('/login_admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Pertama cari admin di tabel Admin
        admin = Admin.query.filter_by(username=username).first()

        # Jika admin ditemukan, cek password
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))  # Arahkan ke dashboard admin
        else:
            flash('Invalid admin credentials')  # Pesan error jika login gagal
    return render_template('login_admin.html')  # Render halaman login admin

# Rute untuk login sebagai user
@app.route('/login_user', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid user credentials')
    return render_template('login_user.html')

# Rute logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_login'))

# Rute dashboard untuk user
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
@role_required('user')
def dashboard():
    school_location = (-7.359787, 108.241471 )  # Lokasi sekolah
    today = date.today()
    now = datetime.now(jakarta_tz)

    # Ambil catatan absensi untuk hari ini
    attendance_today = Attendance.query.filter(
        db.func.date(Attendance.timestamp) == today,
        Attendance.user_id == current_user.id
    ).first()

    # Mengambil hanya 5 catatan absensi terakhir
    attendances = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.timestamp.desc()).limit(5).all()

    # Ubah semua timestamp menjadi zona waktu Jakarta
    for attendance in attendances:
        attendance.timestamp = attendance.timestamp.astimezone(jakarta_tz)

    if request.method == 'POST':
        # Ambil data lokasi pengguna dari form dan hitung jarak ke lokasi sekolah
        user_location = (float(request.form['latitude']), float(request.form['longitude']))
        distance = geodesic(school_location, user_location).meters
        remarks = request.form.get('remarks', '')

        if distance > 100:
            # Jika jarak lebih dari 100 meter
            status = 'Invalid'
            if attendance_today:
                # Jika sudah pernah absen, tambahkan percobaan
                attendance_today.attempts += 1
                if attendance_today.attempts >= 3:
                    attendance_today.status = 'Absent'
                    flash('You have been marked as absent due to too many invalid attempts.')
                db.session.commit()
            else:
                # Catatan absen baru dengan status Invalid
                new_attendance = Attendance(
                    user_id= current_user.id,
                    location=str(user_location),
                    status=status,
                    remarks=remarks,
                    attempts=1
                )
                db.session.add(new_attendance)
                db.session.commit()
                flash('Your attendance attempt was outside the permitted area.')
        else:
            # Jika jarak kurang dari atau sama dengan 100 meter
            if now.time() < datetime.strptime('07:10', '%H:%M').time():
                status = 'On Time'
            else:
                status = 'Late'

            if attendance_today:
                # Update catatan absensi jika sudah ada
                attendance_today.status = status
                attendance_today.location = str(user_location)
                attendance_today.remarks = remarks
                attendance_today.attempts = 0  # Reset attempts
                db.session.commit()
                flash('Attendance record updated successfully.')
            else:
                # Catatan absensi baru
                new_attendance = Attendance(
                    user_id=current_user.id,
                    location=str(user_location),
                    status=status,
                    remarks=remarks,
                    attempts=0  # Karena berada dalam jarak yang diperbolehkan
                )
                db.session.add(new_attendance)
                db.session.commit()
                flash('Attendance recorded successfully.')

    # Tampilkan riwayat absensi pengguna
    return render_template('dashboard.html', attendances=attendances)

@app.route('/history')
@login_required
@role_required('user')
def history():
    # Ambil semua riwayat absensi pengguna yang login
    user_attendances = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.timestamp.desc()).all()

    # Ubah timestamp menjadi zona waktu Jakarta
    for attendance in user_attendances:
        attendance.timestamp = attendance.timestamp.astimezone(jakarta_tz)

    # Kirim data ke template HTML
    return render_template('user_history.html', attendances=user_attendances)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('user')
def profile():
    user = User.query.get(current_user.id)  # Ambil data user berdasarkan id saat ini

    if request.method == 'POST':
        # Perbarui username jika ada perubahan
        new_username = request.form['username']
        if new_username and new_username != user.username:
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.')
                return redirect(url_for('profile'))
            user.username = new_username

        # Perbarui password jika ada perubahan
        new_password = request.form['password']
        if new_password:
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            user.password = hashed_password

        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route('/admin_dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    # Sorting parameters
    sort_by = request.args.get('sort_by', 'nama')  # Default sort by 'nama'
    sort_order = request.args.get('sort_order', 'asc')  # Default order is ascending

    # Query for today's attendance records
    today = date.today()
    attendances_query = Attendance.query.join(User).join(Classes).filter(
        db.func.date(Attendance.timestamp) == today
    )

    # Apply sorting
    if sort_by == 'nama':
        if sort_order == 'asc':
            attendances_query = attendances_query.order_by(User.nama.asc())
        else:
            attendances_query = attendances_query.order_by(User.nama.desc())
    elif sort_by == 'nisn':
        if sort_order == 'asc':
            attendances_query = attendances_query.order_by(User.id.asc())  # Assuming 'id' is NISN
        else:
            attendances_query = attendances_query.order_by(User.id.desc())
    elif sort_by == 'username':
        if sort_order == 'asc':
            attendances_query = attendances_query.order_by(User.username.asc())
        else:
            attendances_query = attendances_query.order_by(User.username.desc())
    elif sort_by == 'name_class':
        if sort_order == 'asc':
            attendances_query = attendances_query.order_by(Classes.nama_kelas.asc())
        else:
            attendances_query = attendances_query.order_by(Classes.nama_kelas.desc())

    attendances = attendances_query.all()

    now = datetime.now()  # Current time for the dashboard
    return render_template(
        'admin_dashboard.html',
        attendances=attendances,
        now=now,
        sort_by=sort_by,
        sort_order=sort_order
    )

@app.route('/admin/students', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_students():
    # Dapatkan filter dari query parameter
    sort_by = request.args.get('sort_by', 'id')  # Default sort by ID
    class_id = request.args.get('class_id', None)  # Filter by class

    # Query daftar siswa berdasarkan filter dan sorting
    if class_id:
        students = User.query.filter_by(classes_id=class_id).order_by(sort_by).all()
    else:
        students = User.query.order_by(sort_by).all()

    # Dapatkan daftar kelas untuk filter
    classes = Classes.query.all()

    return render_template('admin_students.html', students=students, classes=classes)


@app.route('/admin/students/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_add_student():
    if request.method == 'POST':
        # Collect form data
        id = request.form['id']
        nama = request.form['nama']
        classes_id = request.form['classes_id']
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('admin_add_student'))

        # Hash the password and add the user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(id=id, nama=nama, classes_id=classes_id, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Student added successfully.')
        return redirect(url_for('admin_students'))

    # Fetch classes for the dropdown
    classes = Classes.query.all()
    return render_template('admin_add_student.html', classes=classes)


@app.route('/admin/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_edit_student(id):
    student = User.query.get_or_404(id)

    if request.method == 'POST':
        # Update student's data
        student.nama = request.form['nama']
        student.username = request.form['username']
        student.classes_id = request.form['classes_id']

        # Update password if provided
        new_password = request.form.get('password', None)
        if new_password:
            student.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        flash('Student updated successfully.')
        return redirect(url_for('admin_students'))

    # Fetch classes for the dropdown
    classes = Classes.query.all()
    return render_template('admin_edit_student.html', student=student, classes=classes)


@app.route('/admin/students/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_student(id):
    student = User.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully.')
    return redirect(url_for('admin_students'))


@app.route('/edit_attendance/<int:attendance_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_attendance(attendance_id):
    attendance = Attendance.query.get_or_404(attendance_id)

    if request.method == 'POST':
        # Update the attendance record
        attendance.status = request.form['status']
        attendance.remarks = request.form['remarks']
        db.session.commit()
        flash('Attendance record updated successfully.')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_attendance.html', attendance=attendance)



@app.route('/semester_recap', methods=['GET'])
@login_required
@role_required('admin')
def semester_recap():
    from datetime import datetime

    # Get semester and year from query string
    semester = request.args.get('semester', '1')  # Default to semester 1
    year = request.args.get('year', datetime.now().year)  # Default to the current year

    # Determine date range for the selected semester
    if semester == '1':
        start_date = datetime(int(year), 1, 1)
        end_date = datetime(int(year), 6, 30)
    else:
        start_date = datetime(int(year), 7, 1)
        end_date = datetime(int(year), 12, 31)

    # Query attendance records within the semester range
    attendances = Attendance.query.join(User).join(Classes).filter(
        Attendance.timestamp.between(start_date, end_date)
    ).order_by(Attendance.timestamp.asc()).all()

    now = datetime.now()  # Current time for display

    return render_template(
        'semester_recap.html',
        attendances=attendances,
        semester=semester,
        year=int(year),
        now=now
    )



# Error handler untuk 403 Forbidden
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
