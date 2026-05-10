---
title: AI ChatBot
emoji: ✦
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# AI Chat Bot ✦

A responsive, Gemini-styled AI chatbot powered by Mistral AI and FastAPI.

## Live Demo
[View Live on Render](https://ai-chat-bot-dummy-link.onrender.com) *(Update this link after deploying)*

## Features
- **FastAPI Backend**: Fast, lightweight API.
- **Mistral AI Integration**: Uses `langchain-mistralai` for intelligent responses.
- **Responsive UI**: Gemini-inspired light theme that works seamlessly on desktop and mobile.
- **Markdown Support**: Renders tables, code blocks, lists, and bold text.
- **Token Tracking**: Real-time context window token usage monitoring.

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rohansachinpatil/ai-chatbot.git
   cd chatBot
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API Key:**
   Create a `.env` file in the root directory:
   ```env
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

5. **Run the app:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Open `http://localhost:8000` in your browser.

## Deployment (Render)

This project includes a `render.yaml` file for easy deployment on [Render](https://render.com).

1. Push this repository to your GitHub account.
2. Go to [Render Dashboard](https://dashboard.render.com/) -> **Blueprints** -> **New Blueprint Instance**.
3. Connect your GitHub repository.
4. Add your `MISTRAL_API_KEY` when prompted in the Render Dashboard environment variables.
