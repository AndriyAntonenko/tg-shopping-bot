# Technical Guide

This document provides technical details about the TG Shopping Bot, its architecture, and instructions for deployment.

## Architecture

The bot is built using Python and the `pyTelegramBotAPI` (Telebot) library. It uses a polling mechanism to receive updates from Telegram.

### Key Components:
- **Language**: Python 3.12+
- **Framework**: `pyTelegramBotAPI` (Telebot)
- **Database**: SQLite (for storing orders, products, feedback)
- **Storage**: Digital Ocean Spaces (S3-compatible) for storing product images.
- **Containerization**: Docker & Docker Compose

## Prerequisites

To run the bot, you need:
- Docker and Docker Compose installed on the host machine.
- A Telegram Bot Token (from @BotFather).
- A Stripe API Key (for payments).
- Digital Ocean Spaces credentials (for image storage).

## Configuration

The bot is configured via environment variables. Create a `.env` file in the root directory with the following variables:

```env
TG_BOT_KEY=your_bot_token
TG_BOT_NAME=your_bot_username
STRIPE_API_KEY=your_stripe_key
DATABASE_PATH=./data/shop.db

# Digital Ocean Spaces
DO_SPACES_REGION=your_region
DO_SPACES_ENDPOINT=your_endpoint
DO_SPACES_KEY=your_access_key
DO_SPACES_SECRET=your_secret_key
DO_SPACES_BUCKET=your_bucket_name
```

## Deployment on Digital Ocean Droplet

Follow these steps to deploy the bot on a Digital Ocean Droplet (or any Linux server with Docker).

### 1. Connect to the Droplet via SSH

Open your terminal and connect to your server:

```bash
ssh root@your_droplet_ip
```

### 2. Clone the Repository

Clone the project repository to the server:

```bash
git clone <repository_url>
cd <project_directory>
```

### 3. Configure Environment Variables

Create the `.env` file and populate it with your credentials:

```bash
cp .env.example .env
nano .env
```
(Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`)

### 4. Build and Run with Docker Compose

Build the Docker image and start the container in detached mode:

```bash
docker-compose up -d --build
```

### 5. Verify Deployment

Check if the container is running:

```bash
docker-compose ps
```

View logs to ensure the bot started successfully:

```bash
docker-compose logs -f
```

## Database Migrations

The bot automatically applies database migrations on startup using the internal migration system (`src/db/migrations.py`). The database file is stored in the `./data` directory, which is mounted as a volume in `docker-compose.yml` to persist data.
