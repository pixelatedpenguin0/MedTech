from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import Medication, Adherence
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    medications = current_user.medications.all()
    return render_template('dashboard.html', medications=medications)

@bp.route('/adherence/stats')
@login_required
def adherence_stats():
    # Get the last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=6)
    
    # Initialize data structures
    dates = [(start_date + timedelta(days=i)).strftime('%a') for i in range(7)]
    taken_data = [0] * 7
    missed_data = [0] * 7
    
    # Get all medications for the user
    medications = current_user.medications.all()
    
    # For each medication, get adherence records
    for medication in medications:
        adherence_records = Adherence.query.filter(
            Adherence.medication_id == medication.id,
            Adherence.taken_time >= start_date,
            Adherence.taken_time <= end_date
        ).all()
        
        # Count taken and missed doses for each day
        for record in adherence_records:
            day_index = (record.taken_time - start_date).days
            if 0 <= day_index < 7:
                if record.status == 'taken':
                    taken_data[day_index] += 1
                elif record.status == 'missed':
                    missed_data[day_index] += 1
    
    return jsonify({
        'labels': dates,
        'taken': taken_data,
        'missed': missed_data
    })

@bp.route('/test')
@login_required
def test_tab():
    return render_template('test.html')

@bp.route('/external-resources')
@login_required
def external_resources():
    return render_template('external_resources.html')

@bp.route('/mood-tracker')
@login_required
def mood_tracker():
    return render_template('mood_tracker.html') 