# Influencer Content Review

## Overview
The **Influencer Content Review** application is a backend service designed to streamline the review of influencer content submissions (e.g., video topics, draft scripts) against brand briefs for marketing campaigns. It ensures content aligns with campaign goals and brand safety, providing structured feedback on strengths, areas for improvement, and suggestions. The app also generates random brand briefs and submissions for testing or inspiration. Built as a FastAPI application, it processes campaign data from a CSV file and uses Google’s Gemini models for embeddings and language tasks, making it efficient for influencer marketing workflows.

The project is developed as of August 3, 2025, and is intended for influencers and brand managers working with campaigns, such as those for brands like Milanote.

## Features
- **Review Submission**: Submit a `campaignId` and content (text) to receive detailed feedback based on the corresponding brand brief.
- **List Campaigns**: Retrieve a list of all unique campaign IDs from the dataset.
- **Random Brief Generation**: Generate a random brand brief for inspiration or testing.
- **Random Submission Generation**: Generate a random influencer submission for testing purposes.
- **Persistent Index**: Uses LlamaIndex with vector store persistence for fast startup and efficient brief retrieval.

## Technologies Used
- **Python 3.9**: Core programming language for the backend.
- **FastAPI**: High-performance web framework for building the API, enabling asynchronous request handling.
- **LlamaIndex**: Framework for indexing and retrieving brand briefs using vector embeddings, with persistence to disk for efficiency.
- **LangChain**: Library for integrating language models, used to generate feedback with structured prompts.
- **Google Gemini Models**:
  - `embedding-001`: For generating vector embeddings of briefs, enabling efficient retrieval.
  - `gemini-1.5-flash`: For generating feedback and random briefs/submissions.
- **Pandas**: For processing and cleaning CSV data containing campaign activities.
- **Uvicorn**: ASGI server for running the FastAPI application.
- **Pydantic**: For request validation and data modeling in FastAPI endpoints.
- **Docker**: For containerizing the application, ensuring consistent deployment.
- **Virtualenv**: For managing Python dependencies in a local development environment.

## Prerequisites
- **Python 3.9**: Ensure Python 3.9 is installed (matches the error trace provided).
- **Docker**: Required for running the app in a container (optional but recommended for production).
- **Google API Key**: Obtain a Google Generative AI API key for Gemini models from [Google Cloud](https://cloud.google.com).
- **CSV File**: A `data.csv` file with campaign data, including `campaignId`, `message` (for briefs), and `deliverableInput` (for submissions). Update to `milanote-activities.csv` if using a different file.

## Project Structure
```
influencer-content-review/
├── content_review_app.py  # FastAPI backend code
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── data.csv              # Campaign data (replace with milanote-activities.csv if needed)
└── storage/              # Directory for persisted LlamaIndex vector store
```

## Setup Instructions

### Option 1: Running Locally with Virtualenv
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd influencer-content-review
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:
   - Create a `.env` file in the project root:
     ```
     GOOGLE_API_KEY=your-actual-api-key
     ```
   - Alternatively, export the variable:
     ```bash
     export GOOGLE_API_KEY=your-actual-api-key  # On Windows: set GOOGLE_API_KEY=your-actual-api-key
     ```

5. **Ensure CSV File**:
   - Place `data.csv` (or `milanote-activities.csv`) in the project root.
   - Update `content_review_app.py` if using a different filename:
     ```python
     app_instance = ContentReviewApp(csv_path="milanote-activities.csv")
     ```

6. **Run the Application**:
   ```bash
   python content_review_app.py
   ```
   - The FastAPI server will start at `http://localhost:8000`.

### Option 2: Running with Docker
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd influencer-content-review
   ```

2. **Build the Docker Image**:
   ```bash
   docker build -t content-review-app .
   ```

3. **Run the Docker Container**:
   - Using a `.env` file:
     ```bash
     docker run --env-file .env -p 8000:8000 content-review-app
     ```
   - Or passing the environment variable directly:
     ```bash
     docker run -e GOOGLE_API_KEY="your-actual-api-key" -p 8000:8000 content-review-app
     ```

4. **Ensure CSV File**:
   - The `Dockerfile` copies `data.csv`. If using `milanote-activities.csv`, update the `Dockerfile`:
     ```dockerfile
     COPY milanote-activities.csv .
     ```
     - And update `content_review_app.py` as noted above.

### API Endpoints
The application exposes the following endpoints at `http://localhost:8000`:
- **POST `/review_submission`**:
  - **Request**: JSON with `{ "campaign_id": "string", "submission": "string" }`
  - **Response**: JSON with `{ "campaign_id": "string", "brief": "string", "submission": "string", "feedback": "string" }`
  - **Example**:
    ```bash
    curl -X POST "http://localhost:8000/review_submission" -H "Content-Type: application/json" -d '{"campaign_id": "your_campaign_id", "submission": "Sample influencer content"}'
    ```
- **GET `/list_campaigns`**:
  - **Response**: JSON with `{ "campaign_ids": ["string", ...] }`
  - **Example**:
    ```bash
    curl "http://localhost:8000/list_campaigns"
    ```
- **GET `/random_brief`**:
  - **Response**: JSON with `{ "brief": "string" }`
  - **Example**:
    ```bash
    curl "http://localhost:8000/random_brief"
    ```
- **GET `/random_submission`**:
  - **Response**: JSON with `{ "submission": "string" }`
  - **Example**:
    ```bash
    curl "http://localhost:8000/random_submission"
    ```

## Usage
1. **Start the Server**:
   - Use either the virtualenv or Docker method above.
2. **Interact with the API**:
   - Use tools like `curl`, Postman, or a custom frontend to send requests to the endpoints.
   - For `/review_submission`, select a `campaignId` from `/list_campaigns` and provide a submission text.
   - Use `/random_brief` or `/random_submission` to generate sample content for testing.
3. **Feedback Format**:
   - The `/review_submission` endpoint returns feedback in a structured format:
     ```
     ### Feedback
     #### Strengths
     - [List strengths]
     #### Areas for Improvement
     - [List areas needing improvement]
     #### Suggestions
     - [List specific suggestions]
     ```

## Notes
- **Persistence**: The LlamaIndex vector store is persisted to the `./storage` directory, ensuring fast startup after the initial index creation.
- **Security**: Store the `GOOGLE_API_KEY` securely in a `.env` file or secrets manager for production use.
- **CSV File**: Ensure the CSV file has columns `campaignId`, `message`, and `deliverableInput`. Update the filename in the code if different from `data.csv`.
- **Production**:
  - Use Gunicorn with Uvicorn for better performance: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker content_review_app:app`.
  - Monitor Google API quota usage for Gemini models.
  - Consider adding CORS middleware for frontend integration:
    ```python
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(CORSMiddleware, allow_origins=["http://<frontend-url>"], allow_methods=["*"], allow_headers=["*"])
    ```
- **Troubleshooting**:
  - Ensure the Google API key is valid and has access to Gemini models.
  - Verify the CSV file exists and contains valid data.
  - Check logs for API errors or dependency issues.

## Contributing
Contributions are welcome! Please submit issues or pull requests to the repository. Ensure code follows PEP 8 and includes tests for new features.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.