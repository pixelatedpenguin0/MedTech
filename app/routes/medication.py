from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Medication, Reminder, Adherence
from app import db
import requests
from datetime import datetime, time, timedelta
import pytesseract
from PIL import Image
import io
import json
import os

bp = Blueprint('medication', __name__)

# Load mock pharmacy data
def load_pharmacy_data():
    try:
        with open('prices.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

pharmacy_data = load_pharmacy_data()

# GoodRx API configuration
GOODRX_API_KEY = os.environ.get('GOODRX_API_KEY', 'your-api-key-here')
GOODRX_API_URL = "https://api.goodrx.com/v1/prices"

def get_rxcui(drug_name):
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    response = requests.get(url)
    if response.status_code == 200:
        rxcui = response.json().get('idGroup', {}).get('rxnormId', [None])[0]
        return rxcui
    return None

def get_fda_label(drug_name):
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:\"{drug_name}\"&limit=1"
    response = requests.get(url)
    if response.status_code == 200 and 'results' in response.json():
        return response.json()['results'][0]
    return None

def get_medlineplus_summary(rxcui):
    if not rxcui:
        return None
    url = f"https://connect.medlineplus.gov/service?mainSearchCriteria.v.c={rxcui}&mainSearchCriteria.v.cs=2.16.840.1.113883.6.88&knowledgeResponseType=application/json"
    response = requests.get(url)
    if response.status_code == 200 and 'feed' in response.json():
        entries = response.json()['feed'].get('entry', [])
        if entries:
            return entries[0].get('summary', '')
    return None

def get_medication_prices(medication_name):
    headers = {
        'Authorization': f'Bearer {GOODRX_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'name': medication_name,
        'form': 'tablet',  # You can make this dynamic based on the medication
        'quantity': 30,    # You can make this dynamic based on the prescription
    }
    
    try:
        response = requests.get(GOODRX_API_URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback to mock data if API fails
            return get_mock_prices(medication_name)
    except Exception as e:
        print(f"Error fetching prices from GoodRx: {str(e)}")
        return get_mock_prices(medication_name)

def get_mock_prices(medication_name):
    # Mock data for testing
    mock_data = {
        "Lipitor 20mg": [
            {"pharmacy": "CVS Pharmacy", "price": 42.99, "form": "tablet", "quantity": 30},
            {"pharmacy": "Walmart", "price": 29.49, "form": "tablet", "quantity": 30},
            {"pharmacy": "Walgreens", "price": 47.00, "form": "tablet", "quantity": 30}
        ],
        "Ibuprofen 200mg": [
            {"pharmacy": "Costco", "price": 8.99, "form": "tablet", "quantity": 30},
            {"pharmacy": "Target Pharmacy", "price": 11.49, "form": "tablet", "quantity": 30}
        ],
        "Metformin 500mg": [
            {"pharmacy": "CVS Pharmacy", "price": 15.99, "form": "tablet", "quantity": 30},
            {"pharmacy": "Walgreens", "price": 18.50, "form": "tablet", "quantity": 30},
            {"pharmacy": "Rite Aid", "price": 14.99, "form": "tablet", "quantity": 30}
        ]
    }
    
    return mock_data.get(medication_name, [])

@bp.route('/medications')
@login_required
def list_medications():
    medications = current_user.medications.all()
    return render_template('medication/list.html', medications=medications)

@bp.route('/medications/add', methods=['GET', 'POST'])
@login_required
def add_medication():
    if request.method == 'POST':
        name = request.form['name']
        dosage = request.form['dosage']
        frequency = request.form['frequency']
        notes = request.form.get('notes', '')
        total_doses = int(request.form.get('total_doses', 0))
        
        medication = Medication(
            name=name,
            dosage=dosage,
            frequency=frequency,
            notes=notes,
            total_doses=total_doses,
            remaining_doses=total_doses,
            user_id=current_user.id
        )
        db.session.add(medication)
        db.session.commit()
        
        # Add reminders if specified
        for i in range(1, 5):  # Handle up to 4 reminder times
            reminder_time = request.form.get(f'reminder_time_{i}')
            if reminder_time:
                reminder_time = datetime.strptime(reminder_time, '%H:%M').time()
                days = request.form.get(f'reminder_days_{i}', '')
                
                reminder = Reminder(
                    medication_id=medication.id,
                    time=reminder_time,
                    days=days
                )
                db.session.add(reminder)
        
        db.session.commit()
        flash('Medication added successfully!')
        return redirect(url_for('medication.list_medications'))
    
    # NEW: Get prefill values from query params
    name = request.args.get('name', '')
    price = request.args.get('price', '')
    return render_template('medication/add.html', name=name, price=price)

@bp.route('/medications/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medication(id):
    medication = Medication.query.get_or_404(id)
    if medication.user_id != current_user.id:
        flash('You do not have permission to edit this medication')
        return redirect(url_for('medication.list_medications'))
    
    if request.method == 'POST':
        medication.name = request.form['name']
        medication.dosage = request.form['dosage']
        medication.frequency = request.form['frequency']
        medication.notes = request.form.get('notes', '')
        
        db.session.commit()
        flash('Medication updated successfully!')
        return redirect(url_for('medication.list_medications'))
    
    return render_template('medication/edit.html', medication=medication)

@bp.route('/medications/<int:id>/delete', methods=['POST'])
@login_required
def delete_medication(id):
    medication = Medication.query.get_or_404(id)
    if medication.user_id != current_user.id:
        flash('You do not have permission to delete this medication')
        return redirect(url_for('medication.list_medications'))
    
    try:
        # Delete associated reminders and adherence records first
        Reminder.query.filter_by(medication_id=medication.id).delete()
        Adherence.query.filter_by(medication_id=medication.id).delete()
        
        # Then delete the medication
        db.session.delete(medication)
        db.session.commit()
        flash('Medication deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting medication. Please try again.')
        print(f"Error deleting medication: {str(e)}")
    
    return redirect(url_for('medication.list_medications'))

@bp.route('/medications/ocr', methods=['POST'])
@login_required
def process_ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))
    text = pytesseract.image_to_string(image)
    
    # Extract medication name from OCR text
    # This is a simple implementation - you might want to enhance it
    medication_name = text.split('\n')[0].strip()
    
    return jsonify({'medication_name': medication_name})

@bp.route('/medications/drug-info/<name>')
@login_required
def get_drug_info(name):
    # Query openFDA API
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{name}&limit=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return jsonify(data['results'][0])
    
    return jsonify({'error': 'Drug information not found'}), 404

@bp.route('/medications/<int:id>/adherence', methods=['POST'])
@login_required
def record_adherence(id):
    medication = Medication.query.get_or_404(id)
    if medication.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    status = request.form.get('status')
    if status not in ['taken', 'missed', 'skipped']:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Update medication counts
    if status == 'taken':
        medication.taken_doses += 1
        medication.remaining_doses = max(0, medication.remaining_doses - 1)
    elif status == 'missed':
        medication.missed_doses += 1
    
    # Record adherence
    adherence = Adherence(
        medication_id=medication.id,
        status=status
    )
    db.session.add(adherence)
    db.session.commit()
    
    return jsonify({
        'message': 'Adherence recorded successfully',
        'taken_doses': medication.taken_doses,
        'missed_doses': medication.missed_doses,
        'remaining_doses': medication.remaining_doses
    })

@bp.route('/medications/stats')
@login_required
def medication_stats():
    # Get the last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=6)
    
    # Initialize data structures
    dates = [(start_date + timedelta(days=i)).strftime('%a') for i in range(7)]
    actual_data = [0] * 7
    ideal_data = [0] * 7
    
    # Get all medications for the user
    medications = current_user.medications.all()
    
    # For each medication, calculate ideal and actual intake
    for medication in medications:
        freq = medication.frequency

        if freq == 'Once daily':
            for i in range(7):
                ideal_data[i] += 1
        elif freq == 'Twice daily':
            for i in range(7):
                ideal_data[i] += 2
        elif freq == 'Three times daily':
            for i in range(7):
                ideal_data[i] += 3
        elif freq == 'Four times daily':
            for i in range(7):
                ideal_data[i] += 4
        elif freq == 'Every 6 hours':
            for i in range(7):
                ideal_data[i] += 4
        elif freq == 'Every 8 hours':
            for i in range(7):
                ideal_data[i] += 3
        elif freq == 'Every 12 hours':
            for i in range(7):
                ideal_data[i] += 2
        elif freq == 'After every 2 days':
            for i in range(7):
                if i % 2 == 0:
                    ideal_data[i] += 1
        elif freq == 'After every 7 days':
            ideal_data[0] += 1
        # (You can add more custom logic for other frequencies if needed)

        # Get actual adherence records
        adherence_records = Adherence.query.filter(
            Adherence.medication_id == medication.id,
            Adherence.taken_time >= start_date,
            Adherence.taken_time <= end_date,
            Adherence.status == 'taken'
        ).all()
        
        # Count actual taken doses for each day
        for record in adherence_records:
            day_index = (record.taken_time - start_date).days
            if 0 <= day_index < 7:
                actual_data[day_index] += 1
    
    return jsonify({
        'labels': dates,
        'actual': actual_data,
        'ideal': ideal_data
    })

@bp.route('/medications/info')
@login_required
def medication_info():
    return render_template('medication/info.html')

@bp.route('/medications/search')
@login_required
def search_medication():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # Get RxCUI for the medication
    rxcui = get_rxcui(query)
    
    # Get FDA information
    fda_info = get_fda_label(query)
    
    # Get MedlinePlus summary
    medline_summary = get_medlineplus_summary(rxcui) if rxcui else None
    
    # Format the response
    results = []
    
    if fda_info:
        openfda = fda_info.get('openfda', {})
        results.append({
            'name': openfda.get('brand_name', [''])[0],
            'generic_name': openfda.get('generic_name', [''])[0],
            'manufacturer': openfda.get('manufacturer_name', [''])[0],
            'route': openfda.get('route', [''])[0],
            'substance': openfda.get('substance_name', [''])[0],
            'warnings': fda_info.get('warnings', [''])[0] if fda_info.get('warnings') else '',
            'adverse_reactions': fda_info.get('adverse_reactions', [''])[0] if fda_info.get('adverse_reactions') else '',
            'drug_interactions': fda_info.get('drug_interactions', [''])[0] if fda_info.get('drug_interactions') else '',
            'indications_and_usage': fda_info.get('indications_and_usage', [''])[0] if fda_info.get('indications_and_usage') else '',
            'dosage_and_administration': fda_info.get('dosage_and_administration', [''])[0] if fda_info.get('dosage_and_administration') else '',
            'patient_summary': medline_summary,
            'source': 'FDA + MedlinePlus'
        })
    
    # Add RxNorm data if available
    if rxcui:
        rxnorm_url = f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={query}"
        rxnorm_response = requests.get(rxnorm_url)
        if rxnorm_response.status_code == 200:
            rxnorm_results = rxnorm_response.json().get('drugGroup', {}).get('conceptGroup', [])
            for group in rxnorm_results:
                if 'conceptProperties' in group:
                    for concept in group['conceptProperties']:
                        results.append({
                            'name': concept.get('name', ''),
                            'generic_name': concept.get('synonym', ''),
                            'source': 'RxNorm'
                        })
    
    return jsonify(results)

@bp.route('/medications/details/<name>')
@login_required
def medication_details(name):
    # Get RxCUI for the medication
    rxcui = get_rxcui(name)
    
    # Get FDA information
    fda_info = get_fda_label(name)
    
    # Get MedlinePlus summary
    medline_summary = get_medlineplus_summary(rxcui) if rxcui else None
    
    if fda_info:
        openfda = fda_info.get('openfda', {})
        details = {
            'name': openfda.get('brand_name', [''])[0],
            'generic_name': openfda.get('generic_name', [''])[0],
            'manufacturer': openfda.get('manufacturer_name', [''])[0],
            'route': openfda.get('route', [''])[0],
            'substance': openfda.get('substance_name', [''])[0],
            'warnings': fda_info.get('warnings', [''])[0] if fda_info.get('warnings') else '',
            'adverse_reactions': fda_info.get('adverse_reactions', [''])[0] if fda_info.get('adverse_reactions') else '',
            'drug_interactions': fda_info.get('drug_interactions', [''])[0] if fda_info.get('drug_interactions') else '',
            'dosage_and_administration': fda_info.get('dosage_and_administration', [''])[0] if fda_info.get('dosage_and_administration') else '',
            'clinical_pharmacology': fda_info.get('clinical_pharmacology', [''])[0] if fda_info.get('clinical_pharmacology') else '',
            'indications_and_usage': fda_info.get('indications_and_usage', [''])[0] if fda_info.get('indications_and_usage') else '',
            'contraindications': fda_info.get('contraindications', [''])[0] if fda_info.get('contraindications') else '',
            'patient_summary': medline_summary,
            'source': 'FDA + MedlinePlus'
        }
        return jsonify(details)
    
    return jsonify({'error': 'Medication not found'}), 404

@bp.route('/medications/prices')
@login_required
def medication_prices():
    return render_template('medication/prices.html')

@bp.route('/medications/search_prices')
@login_required
def search_prices():
    medication = request.args.get('medication')
    
    if not medication:
        return jsonify({'error': 'Missing medication name'}), 400
    
    # Get prices from GoodRx API
    prices = get_medication_prices(medication)
    
    # Sort prices by lowest first
    if isinstance(prices, list):
        prices.sort(key=lambda x: x['price'])
    
    return jsonify(prices)

@bp.route('/medications/<int:id>/reset_doses', methods=['POST'])
@login_required
def reset_doses(id):
    medication = Medication.query.get_or_404(id)
    if medication.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    medication.remaining_doses = medication.total_doses
    db.session.commit()
    return jsonify({
        'message': 'Doses reset successfully',
        'remaining_doses': medication.remaining_doses,
        'name': medication.name
    }) 