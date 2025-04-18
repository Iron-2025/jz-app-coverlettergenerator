from flask import Flask, render_template, request, jsonify, url_for
import os
import PyPDF2
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from openai import OpenAI
import secrets

load_dotenv()

app = Flask(__name__, 
    static_url_path='/static',
    static_folder='static'
)

# Configure a secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Ensure static folder exists
os.makedirs('static/images', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_stream):
    """Extracts text from a PDF file stream."""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_text_from_txt(file_stream):
    """Extracts text from a TXT file stream."""
    try:
        return file_stream.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return None

@app.route('/')
def index():
    """Renders the main landing page."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_cover_letter():
    """Handles the cover letter generation request."""
    try:
        # Get data from the request
        resume_text_area = request.form.get('resume_text', '').strip()
        job_desc_text_area = request.form.get('job_description_text', '').strip()
        resume_file = request.files.get('resume_file')
        job_desc_file = request.files.get('job_description_file')

        final_resume_text = ""
        final_job_desc_text = ""
        error_message = None

        # Process Resume Input
        if resume_file and resume_file.filename and allowed_file(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            if filename.lower().endswith('.pdf'):
                final_resume_text = extract_text_from_pdf(resume_file.stream)
                if final_resume_text is None:
                    error_message = "Error processing uploaded resume PDF."
            elif filename.lower().endswith('.txt'):
                final_resume_text = extract_text_from_txt(resume_file.stream)
                if final_resume_text is None:
                    error_message = "Error processing uploaded resume TXT file."
            resume_file.stream.seek(0)
        elif resume_text_area:
            final_resume_text = resume_text_area
        else:
            error_message = "Please provide resume text or upload a valid .txt/.pdf file."

        # Process Job Description Input
        if not error_message:
            if job_desc_file and job_desc_file.filename and allowed_file(job_desc_file.filename):
                filename = secure_filename(job_desc_file.filename)
                if filename.lower().endswith('.pdf'):
                    final_job_desc_text = extract_text_from_pdf(job_desc_file.stream)
                    if final_job_desc_text is None:
                        error_message = "Error processing uploaded job description PDF."
                elif filename.lower().endswith('.txt'):
                    final_job_desc_text = extract_text_from_txt(job_desc_file.stream)
                    if final_job_desc_text is None:
                        error_message = "Error processing uploaded job description TXT file."
                job_desc_file.stream.seek(0)
            elif job_desc_text_area:
                final_job_desc_text = job_desc_text_area
            else:
                error_message = "Please provide job description text or upload a valid .txt/.pdf file."

        # Validation
        if error_message:
            return jsonify({'error': error_message}), 400
        if not final_resume_text or not final_job_desc_text:
            return jsonify({'error': 'Failed to get content from resume or job description.'}), 400

        # Call OpenAI API
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'Server configuration error: Missing API key.'}), 500

        client = OpenAI(api_key=api_key)
        generated_letter = "Failed to generate cover letter."

        try:
            prompt = f"""
            You are an expert career advisor helping write a professional cover letter.
            Generate a tailored cover letter based on the following resume and job description.
            The tone should be professional, enthusiastic, and specific to the job.
            Highlight relevant skills and experiences from the resume that match the job requirements.
            Keep the letter concise and focused, typically 3-4 paragraphs.
            Address it to the "Hiring Manager" unless a specific name is found in the job description.
            Do not include placeholders like "[Your Name]" or "[Company Name]" unless they are clearly part of the job description itself.

            --- Resume ---
            {final_resume_text}

            --- Job Description ---
            {final_job_desc_text}

            --- Generated Cover Letter ---
            """

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes professional cover letters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            generated_letter = response.choices[0].message.content.strip()

        except Exception as api_error:
            error_detail = str(api_error)
            if "authentication" in error_detail.lower():
                return jsonify({'error': 'Authentication error with AI service. Check API key.'}), 500
            elif "rate limit" in error_detail.lower():
                return jsonify({'error': 'AI service rate limit exceeded. Please try again later.'}), 429
            else:
                return jsonify({'error': 'Failed to generate cover letter due to an AI service issue.'}), 503

        return jsonify({'cover_letter': generated_letter})

    except Exception as e:
        print(f"Error during generation: {e}")
        return jsonify({'error': 'An unexpected error occurred during generation.'}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', debug=debug_mode, port=5000)
