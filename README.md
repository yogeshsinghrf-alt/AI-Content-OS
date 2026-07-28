# AI Content OS

AI Content OS is a full-stack Generative AI application that discovers relevant industry news and transforms it into structured, platform-specific social media content.

It supports AI, Telecom, and Marketing topics and generates content for LinkedIn, X, Instagram, editorial visuals, infographics, branded PDF reports, and email delivery.

## Live Application

- Frontend: https://ai-content-os-lake.vercel.app
- Backend API: https://ai-content-os-api.onrender.com
- API Documentation: https://ai-content-os-api.onrender.com/docs

## Project Overview

AI Content OS was created to simplify the process of discovering industry news and converting it into professional social media content.

The platform:

1. Collects articles and updates from multiple online sources.
2. Uses Google Gemini to analyse and transform the source material.
3. Produces content tailored for different social platforms.
4. Saves generated packages to history.
5. Creates branded PDF reports.
6. Sends HTML emails with PDF attachments.
7. Includes a scheduled daily content-generation pipeline.

## Key Features

- AI-powered content generation using Google Gemini
- AI, Telecom, and Marketing topic selection
- LinkedIn post generation
- X post generation
- Instagram caption generation
- Editorial headline and subtitle generation
- Hero-image prompt generation
- Infographic content and visual directions
- Content history and search
- Reload and delete saved content
- Branded PDF export
- HTML email delivery through Resend
- Daily scheduling with APScheduler
- Responsive Next.js dashboard
- FastAPI REST backend
- Production deployment using Vercel and Render

## Technology Stack

### Frontend

- Next.js
- React
- TypeScript
- CSS
- Vercel

### Backend

- Python
- FastAPI
- Uvicorn
- Google Gen AI SDK
- APScheduler
- ReportLab
- Resend
- Beautiful Soup
- Feedparser
- Render

### Development and Deployment

- Git
- GitHub
- VS Code
- REST APIs
- Environment-variable configuration
- CORS configuration

## Application Architecture

```text
News and RSS Sources
        |
        v
FastAPI Source Collection
        |
        v
Google Gemini Content Generation
        |
        v
Structured Content Package
        |
        +------> Next.js Dashboard
        |
        +------> JSON History
        |
        +------> Branded PDF
        |
        +------> Resend Email
        |
        +------> Scheduled Daily Pipeline