# PDF Chat Assistant

A web application that allows users to upload PDF documents and ask questions about their content using AWS Bedrock and Claude AI.

## Features

- **PDF Upload**: Drag and drop or browse to upload PDF files
- **Text Extraction**: Automatically extracts text from uploaded PDFs
- **AI Chat**: Ask questions about the PDF content using Claude AI
- **Session Management**: Maintains chat history during the session
- **Responsive Design**: Works on desktop and mobile devices

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with your AWS credentials:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual credentials:

```env
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# Claude Model Configuration
MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

**Alternative Methods:**
- **AWS CLI**: `aws configure` (will use default credential chain)
- **IAM Roles**: If running on EC2 with proper IAM role attached

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Upload PDF**: Click "Choose File" or drag and drop a PDF file
2. **Wait for Processing**: The app will extract text from your PDF
3. **Start Chatting**: Ask questions about the PDF content
4. **Reset Session**: Click "Reset Session" to upload a new PDF

## API Endpoints

- `GET /` - Main application page
- `POST /upload` - Upload PDF file
- `POST /chat` - Send chat message
- `POST /reset` - Reset session

## File Structure

```
├── app.py              # Flask application
├── config.py           # AWS Bedrock configuration
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Frontend interface
└── uploads/           # Temporary file storage (auto-created)
```

## Requirements

- Python 3.7+
- AWS Account with Bedrock access
- Valid AWS credentials configured

## Troubleshooting

- **AWS Credentials**: Ensure AWS credentials are properly configured
- **Bedrock Access**: Make sure your AWS account has access to Bedrock
- **Model Access**: Verify you have access to the Claude model in your region
- **File Size**: Maximum file size is 16MB