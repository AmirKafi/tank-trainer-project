# Tank Trainer Project

This project is a showcase of my work, demonstrating various aspects of software development, including backend services, event-driven architecture, and database management. It is not intended to be used as a tool or library by others but serves as an example of my skills and expertise.

## Features

- **Event-Driven Architecture**: Implements a message bus for handling commands and events.
- **Database Integration**: Uses SQLAlchemy for ORM and PostgreSQL as the database.
- **Redis Caching**: Includes Redis for caching and OTP management.
- **RabbitMQ Messaging**: Utilizes RabbitMQ for message brokering.
- **RESTful API**: Built with FastAPI to expose endpoints for various operations.
- **Authentication**: JWT-based authentication with OTP verification.
- **Dockerized Setup**: Fully containerized using Docker and Docker Compose.

## Project Structure

The project is organized into the following main directories:

- `adapters/`: Contains repository implementations and other adapter components.
- `domains/`: Defines domain models and business logic.
- `entry_points/`: Includes the main application entry point.
- `events/`: Defines commands and events for the message bus.
- `exceptions/`: Custom exception classes.
- `helpers/`: Utility functions and helpers.
- `messaging/`: Message bus and RabbitMQ integration.
- `services/`: Core services and handlers.

## Running the Project

### Prerequisites

- Docker and Docker Compose installed on your system.

### Steps

1. Build and run the application:
   ```bash
   docker compose up --build
   ```

2. Access the application at [http://localhost:8000](http://localhost:8000).

## Notes

- This project is for demonstration purposes only and is not intended for production use.
- For more details on the Docker setup, refer to `README.Docker.md`.

## Contact

If you have any questions or feedback, feel free to reach out.

# پروژه کارآموزی تانک

این پروژه صرفا یک پروژه نمایشی برای نشون دادن کار هاییه که انجام دادم و ابزار هایی که باهاشون کار کردم

## ویژگی‌ها

- **معماری رویداد محور**: پیاده‌سازی یک اتوبوس پیام برای مدیریت دستورات و رویدادها.
- **یکپارچگی پایگاه داده**: استفاده از SQLAlchemy برای ORM و PostgreSQL به عنوان پایگاه داده.
- **کشینگ Redis**: شامل Redis برای کشینگ و مدیریت OTP.
- **پیام‌رسانی RabbitMQ**: استفاده از RabbitMQ برای مدیریت پیام‌ها.
- **API RESTful**: ساخته شده با FastAPI برای ارائه نقاط پایانی مختلف.
- **احراز هویت**: احراز هویت مبتنی بر JWT با تأیید OTP.
- **راه‌اندازی Dockerized**: به طور کامل با استفاده از Docker و Docker Compose کانتینری شده است.

## ساختار پروژه

پروژه به صورت زیر سازماندهی شده است:

- `adapters/`: شامل پیاده‌سازی‌های مخزن و سایر اجزای آداپتور.
- `domains/`: تعریف مدل‌های دامنه و منطق کسب‌وکار.
- `entry_points/`: شامل نقطه ورود اصلی برنامه.
- `events/`: تعریف دستورات و رویدادها برای اتوبوس پیام.
- `exceptions/`: کلاس‌های استثنای سفارشی.
- `helpers/`: توابع و ابزارهای کمکی.
- `messaging/`: اتوبوس پیام و یکپارچگی RabbitMQ.
- `services/`: خدمات اصلی و هندلرها.

## اجرای پروژه

### پیش‌نیازها

- نصب Docker و Docker Compose بر روی سیستم شما.

### مراحل

1. ساخت و اجرای برنامه:
   ```bash
   docker compose up --build
   ```

2. دسترسی به برنامه در [http://localhost:8000](http://localhost:8000).

## یادداشت‌ها

- این پروژه فقط برای اهداف نمایشی است و برای استفاده در محیط تولید مناسب نیست.
- برای جزئیات بیشتر در مورد تنظیمات Docker، به `README.Docker.md` مراجعه کنید.

## تماس

اگر سوال یا بازخوردی دارید، لطفاً با من تماس بگیرید.