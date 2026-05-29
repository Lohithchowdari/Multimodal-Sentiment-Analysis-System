from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Prediction
from services import GroqService, OCRService, AudioService, EmailService, mail
import os
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
import io

app = Flask(__name__)
app.config.from_object(Config)
#dlchowdari@gmail.com
# Initialize extensions
db.init_app(app)
mail.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize AI services
groq_service = None
if app.config['GROQ_API_KEY']:
    groq_service = GroqService(app.config['GROQ_API_KEY'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page"""
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    total_analyses = Prediction.query.filter_by(user_id=current_user.id).count()
    positive_count = Prediction.query.filter_by(user_id=current_user.id, sentiment='positive').count()
    neutral_count = Prediction.query.filter_by(user_id=current_user.id, sentiment='neutral').count()
    negative_count = Prediction.query.filter_by(user_id=current_user.id, sentiment='negative').count()
    
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total=total_analyses,
                         positive=positive_count,
                         neutral=neutral_count,
                         negative=negative_count,
                         recent=recent_predictions)

@app.route('/text-analysis', methods=['GET', 'POST'])
@login_required
def text_analysis():
    """Text sentiment analysis"""
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        
        if not text:
            flash('Please enter some text to analyze', 'error')
            return redirect(url_for('text_analysis'))
        
        if not groq_service:
            flash('AI service not configured', 'error')
            return redirect(url_for('text_analysis'))
        
        # Analyze sentiment
        sentiment, suggestion = groq_service.analyze_sentiment(text, 'text')
        
        # Save prediction
        prediction = Prediction(
            user_id=current_user.id,
            analysis_type='text',
            input_data=text,
            sentiment=sentiment,
            suggestion=suggestion
        )
        
        # Send email if negative
        if sentiment == 'negative':
            email_sent = EmailService.send_alert_email(
                current_user.email,
                sentiment,
                suggestion,
                text
            )
            prediction.email_sent = email_sent
        
        db.session.add(prediction)
        db.session.commit()
        
        return render_template('text_result.html', 
                             text=text,
                             sentiment=sentiment,
                             suggestion=suggestion,
                             prediction_id=prediction.id)
    
    return render_template('text_analysis.html')

@app.route('/image-analysis', methods=['GET', 'POST'])
@login_required
def image_analysis():
    """Image sentiment analysis"""
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image uploaded', 'error')
            return redirect(url_for('image_analysis'))
        
        file = request.files['image']
        
        if file.filename == '':
            flash('No image selected', 'error')
            return redirect(url_for('image_analysis'))
        
        if not groq_service:
            flash('AI service not configured', 'error')
            return redirect(url_for('image_analysis'))
        
        # Extract text from image
        extracted_text = OCRService.extract_text_from_image(file)
        
        if not extracted_text:
            flash('Could not extract text from image. Please ensure the image contains readable text.', 'error')
            return redirect(url_for('image_analysis'))
        
        # Analyze sentiment
        sentiment, suggestion = groq_service.analyze_sentiment(extracted_text, 'image')
        
        # Save prediction
        prediction = Prediction(
            user_id=current_user.id,
            analysis_type='image',
            input_data=extracted_text,
            sentiment=sentiment,
            suggestion=suggestion
        )
        
        # Send email if negative
        if sentiment == 'negative':
            email_sent = EmailService.send_alert_email(
                current_user.email,
                sentiment,
                suggestion,
                extracted_text
            )
            prediction.email_sent = email_sent
        
        db.session.add(prediction)
        db.session.commit()
        
        return render_template('image_result.html',
                             sentiment=sentiment,
                             suggestion=suggestion,
                             prediction_id=prediction.id)
    
    return render_template('image_analysis.html')

@app.route('/audio-analysis', methods=['GET'])
@login_required
def audio_analysis():
    """Audio sentiment analysis page"""
    return render_template('audio_analysis.html')

@app.route('/api/audio-analyze', methods=['POST'])
@login_required
def api_audio_analyze():
    """API endpoint for audio analysis"""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    
    if not groq_service:
        return jsonify({'error': 'AI service not configured'}), 500
    
    # Save audio temporarily
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio.wav')
    audio_file.save(temp_path)
    
    try:
        # Transcribe audio
        transcribed_text = AudioService.transcribe_audio(temp_path)
        
        if not transcribed_text:
            return jsonify({'error': 'Could not transcribe audio. Please speak clearly.'}), 400
        
        # Analyze sentiment
        sentiment, suggestion = groq_service.analyze_sentiment(transcribed_text, 'audio')
        
        # Save prediction
        prediction = Prediction(
            user_id=current_user.id,
            analysis_type='audio',
            input_data=transcribed_text,
            sentiment=sentiment,
            suggestion=suggestion
        )
        
        # Send email if negative
        email_sent = False
        if sentiment == 'negative':
            email_sent = EmailService.send_alert_email(
                current_user.email,
                sentiment,
                suggestion,
                transcribed_text
            )
            prediction.email_sent = email_sent
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'sentiment': sentiment,
            'suggestion': suggestion,
            'prediction_id': prediction.id
        })
        
    except Exception as e:
        print(f"Audio analysis error: {e}")
        return jsonify({'error': 'Failed to process audio'}), 500
    
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/history')
@login_required
def history():
    """Prediction history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('history.html', predictions=predictions)

@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    return render_template('analytics.html')

@app.route('/api/analytics-data')
@login_required
def api_analytics_data():
    """API endpoint for analytics data"""
    days = request.args.get('days', 30, type=int)
    
    # Get predictions from last N days
    start_date = datetime.now(pytz.timezone('Asia/Kolkata')) - timedelta(days=days)
    predictions = Prediction.query.filter(
        Prediction.user_id == current_user.id,
        Prediction.timestamp >= start_date
    ).order_by(Prediction.timestamp.asc()).all()
    
    # Group by date
    daily_data = defaultdict(lambda: {'positive': 0, 'neutral': 0, 'negative': 0})
    
    for pred in predictions:
        date_key = pred.timestamp.strftime('%Y-%m-%d')
        daily_data[date_key][pred.sentiment] += 1
    
    # Convert to list format for Chart.js
    labels = []
    positive_data = []
    neutral_data = []
    negative_data = []
    
    for i in range(days):
        date = (datetime.now(pytz.timezone('Asia/Kolkata')) - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        labels.append(date)
        positive_data.append(daily_data[date]['positive'])
        neutral_data.append(daily_data[date]['neutral'])
        negative_data.append(daily_data[date]['negative'])
    
    # Analysis type distribution
    text_count = Prediction.query.filter_by(user_id=current_user.id, analysis_type='text').count()
    image_count = Prediction.query.filter_by(user_id=current_user.id, analysis_type='image').count()
    audio_count = Prediction.query.filter_by(user_id=current_user.id, analysis_type='audio').count()
    
    return jsonify({
        'timeline': {
            'labels': labels,
            'positive': positive_data,
            'neutral': neutral_data,
            'negative': negative_data
        },
        'distribution': {
            'text': text_count,
            'image': image_count,
            'audio': audio_count
        }
    })

# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin'] = True
            flash('Admin login successful', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin', None)
    flash('Admin logged out', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    users = User.query.all()
    total_users = len(users)
    total_predictions = Prediction.query.count()
    
    user_data = []
    for user in users:
        user_predictions = Prediction.query.filter_by(user_id=user.id).count()
        positive = Prediction.query.filter_by(user_id=user.id, sentiment='positive').count()
        neutral = Prediction.query.filter_by(user_id=user.id, sentiment='neutral').count()
        negative = Prediction.query.filter_by(user_id=user.id, sentiment='negative').count()
        
        user_data.append({
            'user': user,
            'total': user_predictions,
            'positive': positive,
            'neutral': neutral,
            'negative': negative
        })
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_predictions=total_predictions,
                         user_data=user_data)

@app.route('/admin/user/<int:user_id>')
def admin_user_detail(user_id):
    """Admin view specific user"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    user_id = request.view_args['user_id']
    user = User.query.get_or_404(user_id)
    
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.timestamp.desc()).limit(50).all()
    
    return render_template('admin_user_detail.html', user=user, predictions=predictions)

@app.route('/admin/api/user-analytics/<int:user_id>')
def admin_api_user_analytics(user_id):
    """API endpoint for user analytics (admin)"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = request.view_args['user_id']
    days = request.args.get('days', 30, type=int)
    
    start_date = datetime.now(pytz.timezone('Asia/Kolkata')) - timedelta(days=days)
    predictions = Prediction.query.filter(
        Prediction.user_id == user_id,
        Prediction.timestamp >= start_date
    ).order_by(Prediction.timestamp.asc()).all()
    
    daily_data = defaultdict(lambda: {'positive': 0, 'neutral': 0, 'negative': 0})
    
    for pred in predictions:
        date_key = pred.timestamp.strftime('%Y-%m-%d')
        daily_data[date_key][pred.sentiment] += 1
    
    labels = []
    positive_data = []
    neutral_data = []
    negative_data = []
    
    for i in range(days):
        date = (datetime.now(pytz.timezone('Asia/Kolkata')) - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        labels.append(date)
        positive_data.append(daily_data[date]['positive'])
        neutral_data.append(daily_data[date]['neutral'])
        negative_data.append(daily_data[date]['negative'])
    
    return jsonify({
        'labels': labels,
        'positive': positive_data,
        'neutral': neutral_data,
        'negative': negative_data
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)