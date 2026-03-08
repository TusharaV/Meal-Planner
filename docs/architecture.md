# Fridge to Feast — Architecture

## How The App Is Split
Frontend: Built in Lovable (lovable.dev)
Backend: Built with Claude Code (FastAPI + Python)
They talk to each other via API endpoint.

## How They Connect
Local dev: Lovable → ngrok URL → laptop FastAPI
Production: Lovable → Railway URL → FastAPI

## The One Endpoint
POST /suggest
Input: vegetables, stomach, weekday/weekend, meal type, yogurt
Output: 2 meal suggestions + recipes + YouTube links

## How The Claude API Call Works
1. FastAPI receives user inputs from Lovable
2. Builds prompt using meal-rules.md logic
3. Sends to Claude API
4. Claude returns 2 meal suggestions
5. FastAPI formats response as JSON
6. Lovable displays results with YouTube buttons

## Why Lovable for Frontend
Fast beautiful UI without writing HTML/CSS manually.

## Why FastAPI for Backend
Simple Python. Easy to learn. One endpoint needed.

## Version 2 Plans
- Add hooks in .claude/settings.json
- YouTube API for real video thumbnails
- Save favourite meals
- Weekly meal planner view