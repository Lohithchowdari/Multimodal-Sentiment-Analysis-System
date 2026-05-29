from groq import Groq
from flask_mail import Mail, Message
from flask import current_app
import pytesseract
from PIL import Image
import speech_recognition as sr
import os
import io

mail = Mail()

class GroqService:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
    
    def analyze_sentiment(self, text, analysis_type="text"):
        """Analyze sentiment and return classification with suggestion"""
        try:
            prompt = f"""Analyze the following {analysis_type} content and determine the emotional state and mental wellbeing.

Content: "{text}"

Classify this as one of: POSITIVE, NEUTRAL, or NEGATIVE

Consider these factors:
- POSITIVE: Happy, optimistic, motivated, content, grateful, hopeful, excited
- NEUTRAL: Factual, informational, balanced, no strong emotion
- NEGATIVE: Sad, anxious, stressed, depressed, lonely, suicidal thoughts, hopeless, angry

Respond with ONLY the classification word (POSITIVE, NEUTRAL, or NEGATIVE) on the first line.
Then provide a brief, empathetic suggestion or encouragement (2-3 sentences) on the following lines."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an empathetic mental health assistant that analyzes emotional states and provides supportive guidance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            lines = result.split('\n', 1)
            
            sentiment = lines[0].strip().upper()
            suggestion = lines[1].strip() if len(lines) > 1 else "Take care of yourself."
            
            # Validate sentiment
            if sentiment not in ['POSITIVE', 'NEUTRAL', 'NEGATIVE']:
                sentiment = 'NEUTRAL'
                suggestion = "I'm here to support you. How can I help you today?"
            
            return sentiment.lower(), suggestion
            
        except Exception as e:
            print(f"Groq API Error: {e}")
            return 'neutral', "Unable to analyze sentiment at this time. Please try again."
    
    def generate_email_content(self, sentiment, text):
        """Generate supportive email content for negative sentiment"""
        try:
            prompt = f"""A user is experiencing negative emotions based on their message: "{text}"

Write a compassionate, supportive email (3-4 paragraphs) that:
1. Acknowledges their feelings with empathy
2. Provides practical coping strategies
3. Encourages them to seek support if needed
4. Ends with hope and reassurance

Keep it warm, professional, and supportive. Include resources like mental health hotlines if appropriate."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a compassionate mental health support assistant writing supportive emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Groq API Error: {e}")
            return """We noticed you might be going through a difficult time. Your wellbeing matters to us.

Remember that it's okay to not be okay sometimes, and reaching out for support is a sign of strength, not weakness.

If you're experiencing distressing thoughts, please consider talking to someone you trust or contacting a mental health professional.

We're here for you."""


class OCRService:
    @staticmethod
    def extract_text_from_image(image_file):
        """Extract text from image using Tesseract OCR"""
        try:
            # Open image
            image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            return text.strip()
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return None


class AudioService:
    @staticmethod
    def transcribe_audio(audio_file):
        """Transcribe audio to text using speech recognition"""
        try:
            # First, try to convert the audio file to WAV format using pydub
            from pydub import AudioSegment
            
            # Read the audio file
            try:
                # Try reading as WebM
                audio = AudioSegment.from_file(audio_file, format="webm")
            except:
                try:
                    # Try reading as generic audio
                    audio = AudioSegment.from_file(audio_file)
                except:
                    # If all else fails, try as WAV
                    audio = AudioSegment.from_wav(audio_file)
            
            # Convert to WAV format with proper settings
            audio = audio.set_frame_rate(16000).set_channels(1)
            
            # Export to a temporary WAV file
            wav_path = audio_file.replace('.wav', '_converted.wav')
            audio.export(wav_path, format="wav")
            
            # Now use speech recognition on the WAV file
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
            
            # Transcribe
            text = recognizer.recognize_google(audio_data)
            
            # Clean up temporary file
            import os
            if os.path.exists(wav_path):
                os.remove(wav_path)
            
            return text
            
        except sr.UnknownValueError:
            print("Speech Recognition: Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech Recognition Error: {e}")
            return None
        except Exception as e:
            print(f"Audio Processing Error: {e}")
            return None


class EmailService:
    @staticmethod
    def send_alert_email(user_email, sentiment, suggestion, content):
        """Send email alert for negative sentiment detection"""
        try:
            groq_service = GroqService(current_app.config['GROQ_API_KEY'])
            email_body = groq_service.generate_email_content(sentiment, content)
            
            msg = Message(
                subject=f"MindSync AI - Support & Guidance",
                recipients=[user_email],
                html=f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;">
                            <h2 style="color: white; text-align: center;">MindSync AI - We're Here for You</h2>
                        </div>
                        <div style="max-width: 600px; margin: 20px auto; padding: 30px; background: #f9f9f9; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <p style="font-size: 16px; white-space: pre-line;">{email_body}</p>
                            
                            <div style="margin-top: 30px; padding: 20px; background: white; border-radius: 8px; border-left: 4px solid #667eea;">
                                <h3 style="color: #667eea; margin-top: 0;">Emergency Resources</h3>
                                <p><strong>National Suicide Prevention Lifeline (India):</strong> <a href="tel:9152987821">91529 87821</a></p>
                                <p><strong>Vandrevala Foundation:</strong> <a href="tel:18602662345">1860 2662 345</a></p>
                                <p><strong>AASRA:</strong> <a href="tel:2227546669">022 2754 6669</a></p>
                            </div>
                            
                            <p style="margin-top: 30px; text-align: center; color: #666;">
                                <small>This is an automated message from MindSync AI. Your privacy is important to us.</small>
                            </p>
                        </div>
                    </body>
                </html>
                """
            )
            
            mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Email Error: {e}")
            return False