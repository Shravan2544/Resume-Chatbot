from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import os
import json
import uuid
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
from config import bedrock_client, model_id

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def generate_chat_response(query, context):
    '''Generate a response to the user's query using the provided context and model.'''
    prompt = f"""
    Human: The user asked: "{query}".\n\n
    Role:
    You are a Resume Specialist Assistant.
    Task:
    Provide accurate and concise information about the resume holder with showcasing his abilities and skills with the help of documents provided.
    Guidelines:

    - Use the provided documents to answer questions about the resume holder.
    - Focus on the resume holder's skills, experiences, and qualifications.

    Response Style:
    Be concise, clear, and to the point.
    Avoid technical jargon and complex language.
    Do not explain the context of your responses—just provide the answer.
    If references are necessary, include them.

    Answer Format:
    - If the question is about a specific skill or experience, provide a direct answer.
    - If the question is general, provide a brief overview of the resume holder's qualifications.
    - If the question requires a detailed explanation, provide a concise summary.
    - If the question is about a specific document, reference it directly.
    - If the question is about a specific skill, provide a direct answer.
    

    

   

    Context Handling:
    If a question requires additional context for accuracy, ask for it.
    If the question is general and no context is needed, provide a straightforward answer.

    Restrictions:
    Do not provide personal opinions.
    Do not include unnecessary explanations or discussions about the response structure.

    Assistant:
    """
    try:
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": f"{query} \n\nContext: {context}"}],
            })
        )
        
        response_body = json.loads(response['body'].read())
        
        assistant_reply = ""
        if "content" in response_body and len(response_body["content"]) > 0:
            content_item = response_body["content"][0]
            if content_item.get("type") == "text":
                assistant_reply = content_item.get("text", "")
        
        return assistant_reply
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + '_' + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        extracted_text = extract_text_from_pdf(file_path)
        
        session['pdf_text'] = extracted_text
        session['pdf_filename'] = filename
        
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'text_preview': extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text
        })
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    if 'pdf_text' not in session:
        return jsonify({'error': 'No PDF uploaded. Please upload a PDF first.'}), 400
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    context = session['pdf_text']
    if session['chat_history']:
        context += "\n\nPrevious conversation:\n" + "\n".join(session['chat_history'][-10:])
    
    response = generate_chat_response(query, context)
    
    session['chat_history'].append(f"User: {query}")
    session['chat_history'].append(f"Assistant: {response}")
    
    return jsonify({
        'response': response,
        'query': query
    })

@app.route('/reset', methods=['POST'])
def reset_session():
    session.clear()
    return jsonify({'success': True, 'message': 'Session reset successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)