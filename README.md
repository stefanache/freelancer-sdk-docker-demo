# Freelancer SDK Docker Demo

A unofficial dockerized version of the Freelancer.com SDK demo web application, combining:
- [freelancer-sdk-python demo_web_application](https://github.com/freelancer/freelancer-sdk-python/tree/master/examples/demo_web_application)
- [esapyi Docker structure](https://github.com/freelancer/esapyi)

## Features

- Flask web application with Freelancer OAuth integration
- PostgreSQL database for user/project storage
- Docker Compose for easy development and production deployment
- Hot reload in development mode
- Gunicorn for production

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/stefanache/freelancer-sdk-docker-demo.git
cd freelancer-sdk-docker-demo
```

### 2. Configure environment

Under Ubuntu:

- to install python-env use

```bash
sudo apt install python3-dotenv
```

- to find your internal IP use:
  
```bash
hostname -I
```

- to find(cURL-based) my external IP use:
```bash
curl ifconfig.me
```

- to build the environment file:

```bash
cp .env.example .env
nano .env
```

Edit `.env` with your Freelancer API credentials:
- Get [credentials](https://accounts.freelancer.com/) from: https://www.freelancer.com/users/settings/api-credentials

Save with **^O Enter** and exit from nano editor with **^X**

### 3. Start the application

```bash
chmod +x run.sh
./run.sh dev
```

The application will be available at: http://127.0.0.1:5000

## Commands

| Command | Description |
|---------|-------------|
| `./run.sh dev` | Start development server with hot reload |
| `./run.sh prod` | Start production server with gunicorn |
| `./run.sh db` | Start only the database |
| `./run.sh stop` | Stop all containers |
| `./run.sh logs` | View container logs |
| `./run.sh shell` | Open shell in app container |
| `./run.sh clean` | Remove all containers and volumes |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FREELANCER_CLIENT_ID` | Yes | Your Freelancer App Client ID |
| `FREELANCER_CLIENT_SECRET` | Yes | Your Freelancer App Client Secret |
| `SECRET_KEY` | Yes (prod) | Flask secret key for sessions |
| `REDIRECT_URI` | No | OAuth redirect URI (default: http://127.0.0.1:5000/auth_redirect) |
| `FREELANCER_BASE_URL` | No | API base URL (default: https://www.freelancer.com) |
| `FREELANCER_ACCOUNTS_URL` | No | OAuth URL (default: https://accounts.freelancer.com) |

## Using Sandbox (Testing)

To test without affecting real projects, use Freelancer Sandbox.
For life in real-projects, use Freelancer Production.

```bash
# In .env file:
#
# - in sandbox for testing:
FREELANCER_BASE_URL=https://www.freelancer-sandbox.com
FREELANCER_ACCOUNTS_URL=https://accounts.freelancer-sandbox.com
#
# - in production for life:
# In .env file:
FREELANCER_BASE_URL=https://www.freelancer.com
FREELANCER_ACCOUNTS_URL=https://accounts.freelancer.com
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/health` | GET | Health check |
| `/auth` | GET | Start OAuth flow |
| `/auth_redirect` | GET | OAuth callback |
| `/logout` | GET | Logout user |
| `/create_project` | GET/POST | Create new project |
| `/project/<id>/bids` | GET | Get project bids |
| `/award/<bid_id>` | PUT | Award bid |
| `/create_milestone` | POST | Create milestone payment |
| `/pay/<transaction_id>` | POST | Release payment |
| `/projects` | GET | List user projects |

## Project Structure

```
freelancer-sdk-docker-demo/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Docker Compose configuration
├── run.sh                 # Control script
├── .env.example           # Environment template
├── templates/             # HTML templates
│   ├── home.html
│   ├── user.html
│   ├── button.html
│   └── create_project.html
└── README.md
```

## Production Deployment

For production, use the production profile:

```bash
./run.sh prod
```

This will:
- Use gunicorn with 4 workers
- Disable Flask debug mode
- Run without volume mounts (for security)

## Getting Freelancer API Credentials

1. Log in to Freelancer.com
2. Go to Settings → API Credentials
3. Create a new application
4. Set the redirect URI to match your `REDIRECT_URI` environment variable
5. Copy Client ID and Client Secret to `.env`

For more details consult the Freelancer-API/SDK [developer's docs](https://developers.freelancer.com/docs).

## License

MIT License
