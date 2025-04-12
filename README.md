# Autonomous Warehouse Robot System with Web Platform

## Overview
This project implements an autonomous warehouse robot management system with an integrated web platform. It provides a comprehensive solution for controlling and monitoring warehouse robots, mapping warehouse layouts, managing navigation paths, and handling task assignments.

## System Architecture

![System Architecture](https://mermaid.ink/img/pako:eNqNkstOwzAQRX8l8rJCpVUTRxUSbheCRCmwe5Y2Nq1UO8H21KZC-Xfskjy6YMXGc67nztgzmwTEnCXQ82FPYYyMQ0NkLtiyUNxiiJORQQmJxCWOPyTQRO5JzigspQTNB5vFkid0fbC2_5bt8xqQ-zqCau0tbcbfo6dL4I3PfnU0vYgB6DreJROu2CVXJXPeekTV1xesaDQNuZNFo7IwQ5lSaImi6d9BCNQw4YpdcGVLqnhTp-dUBk8eoafI3V3rTJXuPsrnJ9zPqr3TKwN2md-NXI7GQTvZHvQ3LTpntVNCMcvayF5FtIbyzXo_GDWSMXSR9o9XrYUP52EL8kZsbGfDt5tVYwdvaA9kyJFT5Dtj6W1K71zxQ9mTVpXcbl-ISxKhxBnJTY36P5SbcvX0HNeBFNJV-ldamGu4RIKE2siw_QZhe_QrD2z6AzrPuVs)

### Backend Components:
- **FastAPI Web Server**
  - REST API endpoints for robot control and management
  - Authentication and authorization
  - Database integration
  - MQTT client integration
- **PostgreSQL Database**
  - User management
  - Warehouse layout (nodes and edges)
  - Robot status tracking
  - Task management
- **MQTT Broker (Mosquitto)**
  - Real-time communication with robots
  - Publish/subscribe architecture
  - Authentication and ACLs
- **Node-RED**
  - Visual programming for workflow automation
  - Dashboard capabilities
  - MQTT integration for robot monitoring

### Frontend (not included in this codebase):
- Dashboard for robot status monitoring
- Warehouse visualization
- Task creation and management
- User management interface

## Data Model
The system uses a graph-based data model for warehouse navigation:

- **Nodes**: Represent locations in the warehouse
- **Edges**: Define possible paths between nodes with distances
- **Robots**: Physical devices with current location and battery status
- **Tasks**: Work assignments for robots with start/end locations and status

## Installation

### Prerequisites
- Docker and Docker Compose
- PostgreSQL (if running locally)
- Python 3.9+

### Docker Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/warehouse-robot-system.git](https://github.com/OussamaGhz/warehouse-robot-system.git)
   cd warehouse-robot-system
   ```

2. Create a `.env` file with required configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Configure Mosquitto for MQTT:
   ```bash
   cp mosquitto/config/mosquitto.conf.example mosquitto/config/mosquitto.conf
   # Edit mosquitto.conf as needed
   ```

4. Set up Mosquitto authentication:
   ```bash
   docker run --rm -it -v $(pwd)/mosquitto/config:/mosquitto/config eclipse-mosquitto mosquitto_passwd -c /mosquitto/config/password_file mqtt_user
   # Enter password when prompted
   ```

5. Start the services:
   ```bash
   docker-compose up -d
   ```

### Local Development Setup
1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation
The API provides the following endpoints:

### Authentication
- `POST /api/v1/auth/login`: Authenticate user and get access token
- `POST /api/v1/auth/refresh`: Refresh access token
- `POST /api/v1/auth/create-user`: Create a new user (admin only)

### Users
- `GET /api/v1/users/me`: Get current user information
- `GET /api/v1/users/users/admin`: Get admin data (admin only)

### Robots
- `POST /api/v1/robots/{robot_id}/command`: Send command to a robot
- `GET /api/v1/robots/{robot_id}/status`: Get robot status

### LED Control
- `POST /api/v1/led/control`: Control robot LED (on/off)

## Robot Communication Protocol
Communication with robots uses MQTT with the following topic structure:

- Commands: `robot/{robot_id}/commands`
- Status: `robot/{robot_id}/position`
- LED Control: `robot/esp32/commands`
- LED Status: `robot/esp32/state`

## Database Schema
The database includes the following tables:

### Users
- `id`: Primary key
- `username`: Unique username
- `hashed_password`: Securely stored password
- `role`: User role ("admin" or "operator")

### Nodes (Warehouse Locations)
- `id`: Primary key
- `name`: Location name
- `x_pos`: X coordinate
- `y_pos`: Y coordinate

### Edges (Paths)
- `id`: Primary key
- `source_id`: Starting node
- `target_id`: Ending node
- `weight_cm`: Path length in centimeters

### Robots
- `id`: Primary key
- `current_node_id`: Current location
- `battery`: Battery percentage

### Tasks
- `id`: Primary key
- `start_node_id`: Starting location
- `end_node_id`: Destination
- `robot_id`: Assigned robot (nullable)
- `status`: Task status (PENDING, IN_PROGRESS, COMPLETED, FAILED)

## Container Architecture
The system uses Docker Compose with the following services:

- `web`: FastAPI application
- `db`: PostgreSQL database
- `nginx`: Web server and reverse proxy
- `mosquitto`: MQTT broker
- `nodered`: Visual programming tool

## Security
- JWT-based authentication
- Role-based access control
- Secure password hashing
- MQTT authentication and ACLs

## Development

### Adding New Endpoints
1. Create a new file in `endpoints`
2. Define your router and endpoints
3. Include the router in `router.py`

### Adding Database Models
1. Define models in `models`
2. Create corresponding Pydantic schemas in `schemas`
3. Update `Base.metadata.create_all(bind=engine)` in `main.py`

## Troubleshooting

### MQTT Connection Issues
- Check Mosquitto logs: `docker-compose logs mosquitto`
- Verify credentials in `.env` match the password file
- Confirm ACL permissions are correct

### Database Issues
- Check PostgreSQL logs: `docker-compose logs db`
- Verify database URL in `.env`
- Check table creation with `\dt` in psql

## License
MIT License

## Contributors
Ghazi Oussama Soheib
