# 🛍️ TG Shopping Bot

> **A powerful, feature-rich, and user-friendly Telegram bot designed for seamless e-commerce experiences.**

Welcome to the **TG Shopping Bot**! This project provides a complete solution for running a shop directly within Telegram. It allows users to browse products, manage a cart, place orders, and track their status, while administrators have full control over the catalog and order management.

---

## 🌟 Key Features

### 👤 For Users
*   **🛒 Interactive Catalog**: Browse products with ease using a beautiful inline keyboard interface.
*   **📦 Order Management**: Place orders, view order history, and track status updates in real-time.
*   **💳 Secure Payments**: Integrated with Stripe for secure and fast transactions.
*   **🌐 Multi-language Support**: Switch between English and Ukrainian languages instantly.
*   **🗣️ Feedback System**: Send feedback directly to the administration.

### 🛡️ For Administrators
*   **📊 Dashboard**: View pending orders and manage them with a single click.
*   **📝 Content Management**: Add, remove, and update products directly from the bot.
*   **🖼️ Media Support**: Upload product images which are securely stored in Digital Ocean Spaces.
*   **📬 Feedback Loop**: Read and respond to user feedback.

---

## 📚 Documentation

Detailed documentation is available to help you get started and understand the system:

### 📖 User Guide
*   [🇬🇧 English Version](docs/user_guide_en.md)
*   [🇺🇦 Ukrainian Version](docs/user_guide_ua.md)

### ⚙️ Technical Guide
*   [🇬🇧 English Version](docs/tech_guide_en.md)
*   [🇺🇦 Ukrainian Version](docs/tech_guide_ua.md)

---

## 🛠️ Tech Stack

This project is built with modern technologies to ensure performance and reliability:

*   **Language**: 🐍 Python 3.12+
*   **Framework**: 🤖 `pyTelegramBotAPI` (Telebot)
*   **Database**: 🗄️ SQLite
*   **Storage**: ☁️ Digital Ocean Spaces (S3)
*   **Deployment**: 🐳 Docker & Docker Compose

---

## 🚀 Quick Start

1.  **Clone the repo**:
    ```bash
    git clone <repository_url>
    ```
2.  **Configure environment**:
    Copy `.env.example` to `.env` and fill in your API keys.
3.  **Run with Docker**:
    ```bash
    docker-compose up -d --build
    ```

Enjoy your shopping bot! 🎉
