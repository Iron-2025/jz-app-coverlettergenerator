# Cover Letter Generator

A Flask-based web application that generates professional cover letters using AI. The application takes a resume and job description as input (either through text or file upload) and generates a tailored cover letter using OpenAI's GPT model.

## Features

- Upload resume and job description as PDF or TXT files
- Input text directly through text areas
- AI-powered cover letter generation
- Modern and responsive web interface
- Secure file handling and processing

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key

## Environment Variables

Create a `.env` file in the root directory with the following:

```
OPENAI_API_KEY=your_api_key_here
```

## Local Development

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Access the application at `http://localhost:5000`

## Docker Deployment

### Using Docker Compose (Recommended)

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. Access the application at `http://localhost:5000`

### Manual Docker Build

1. Build the Docker image:
   ```bash
   docker build -t cover-letter-generator .
   ```
2. Run the container:
   ```bash
   docker run -p 5000:5000 --env-file .env cover-letter-generator
   ```

## Security Features

- Secure file handling with allowed extensions
- Environment variable based configuration
- Input validation and sanitization
- Error handling and logging
- No persistent storage of uploaded files
- Secure session management

## Project Structure

```
.
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── static/            # Static assets
├── templates/         # HTML templates
└── Dockerfile         # Docker configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 