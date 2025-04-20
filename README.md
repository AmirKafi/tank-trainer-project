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