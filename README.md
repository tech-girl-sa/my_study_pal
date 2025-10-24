# My Study Pal

Study Pal is a smart, AI-powered educational platform designed to help learners organize, understand, and interact with their study materials.
It adapts dynamically to each user’s education level, study goals, and learning needs — providing a personalized and efficient study experience.

![StudyPal Logo](./my_study_pal/static/images/main/logo.png)


# Features

## 👤 User & Onboarding

Guided onboarding flow that collects user’s academic info, goals, and study interests.

AI adapts learning paths, suggestions, and quiz difficulty based on user profile.

## 📚 Subjects & Courses

Create and manage subjects and courses.

Each course is divided into sections, displayed as chat-like learning areas.

Each section stores materials, conversations, and AI-generated content.

## 💬 Interactive Course Sections

Smart chat interface for each section.

Users can ask questions, upload documents, and get AI-generated explanations, summaries, or quizzes.

Chats maintain messages history for more interactive user experience.

Contextual action buttons appear within conversations (e.g., “Summarize”, “Explain more”, “Translate”).

## 📁 Documents Management

Upload and manage course materials in PDF format.

Each document is automatically linked to its subject and course.

Drag-and-drop upload area with modern, responsive design.

## 🧩 Quizzes (in coming versions)

Automatically or manually generate quizzes per course or section.

Track creation date, related course, and easily manage via table view.

Edit or delete quizzes directly from the UI.

## 🧭 Dashboard & Navigation

Modern dashboard design with light and dark section sidebars.

Consistent visual language across pages (Subjects, Courses, Documents, Quizzes).

Pagination, sorting, and filtering options for easy data handling.
.
## 🧱 Tech Stack
### Backend

Django REST Framework (DRF) — clean, modular REST API design.

Organized architecture with separate apps for users, subjects, courses, documents, quizzes, and AI agents.

Integrated filtering, pagination, and custom endpoints (e.g., onboarding, user info, AI agent retrieval).

Docker integration to facilitate sharing and installing the project on multiple machines.

Integrated Swagger documentation to facilitate use of the endpoints.

### Frontend

React + React Router for page-based navigation.

React Query for efficient API data fetching and caching.

CSS Modules for scoped, maintainable component styling.

Formik for forms validation.

frontend project can be found in [this separate repo](https://github.com/tech-girl-sa/my_study_pal_frontend). 

## AI & Smart Features

Intelligent backend integration for document summarization, question answering, and adaptive quiz generation based on 
personal resources.

Personalization logic based on user onboarding responses and activity.

Customisable Settings for Multi-Model LLM Support

### 🧬 LangChain + pgvector Integration  

### **Overview**
Study Pal uses **LangChain** for chain orchestration and **pgvector** for efficient similarity search and context retrieval.  

Each uploaded document is:
1. **Parsed** (PDF)
2. **Split** into chunks
3. **Embedded** into vectors using OpenAI or Hugging Face embeddings
4. **Stored** in PostgreSQL via pgvector

This enables semantic querying and contextual answers during AI interactions.

## 💡 Inspiration

Study Pal was created to make learning smarter and more intuitive — helping students not just store their notes, 
but truly understand and interact with them through AI.


## Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).
use ```docker compose -f docker-compose.local.yml build``` ```docker compose -f docker-compose.local.yml up``` to start
the project. Once backend is running on port 8000, You need to run frontend project to be able to interact with 
the user interface.
