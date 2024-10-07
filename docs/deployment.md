# AI-MOA Deployment Guide

This guide covers the deployment process for AI-MOA in both development and production environments.

## Development Deployment

### Local Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-org/ai-moa.git
   cd ai-moa
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r src/requirements.txt
   ```

4. Configure the application:
   - Copy `src/config.yaml.example` to `src/config.yaml` and update settings
   - Copy `src/workflow-config.yaml.example` to `src/workflow-config.yaml` and customize

5. Run the application:
   ```
   python src/main.py
   ```

### Docker Setup for Development

1. Build the Docker image:
   ```
   docker build -t ai-moa:dev .
   ```

2. Run the container:
   ```
   docker run -p 8000:8000 -v $(pwd)/src:/app/src ai-moa:dev
   ```

## Production Deployment

### Server Requirements

- Linux server (e.g., Ubuntu 20.04 LTS)
- Python 3.9+
- Docker and Docker Compose (optional)
- Nginx (for reverse proxy)
- SSL certificate (e.g., Let's Encrypt)

### Deployment Steps

1. Clone the repository on the production server:
   ```
   git clone https://github.com/your-org/ai-moa.git
   cd ai-moa
   ```

2. Create a production configuration:
   - Copy `src/config.yaml.example` to `src/config.yaml`
   - Update all settings for production environment
   - Ensure sensitive information is properly secured

3. Build the Docker image:
   ```
   docker build -t ai-moa:prod .
   ```

Note: The current configuration uses Huey with in-memory storage. For production deployments with high load or requiring persistence across restarts, consider configuring Huey with Redis or SQLite backend.

4. Create a `docker-compose.prod.yml` file:
   ```yaml
   version: '3.8'
   
   services:
     ai_moa:
       image: ai-moa:prod
       volumes:
         - ./src:/app/src
         - ./logs:/app/logs
       environment:
         - ENVIRONMENT=production
       restart: always
       command: gunicorn src.main:app --workers 4 --bind 0.0.0.0:8000
   ```

5. Start the application:
   ```
   docker-compose -f docker-compose.prod.yml up -d
   ```

6. Set up Nginx as a reverse proxy:
   - Install Nginx: `sudo apt install nginx`
   - Create a new Nginx configuration file:
     ```
     sudo nano /etc/nginx/sites-available/ai-moa
     ```
   - Add the following configuration:
     ```nginx
     server {
         listen 80;
         server_name your-domain.com;
     
         location / {
             proxy_pass http://localhost:8000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
     }
     ```
   - Enable the site:
     ```
     sudo ln -s /etc/nginx/sites-available/ai-moa /etc/nginx/sites-enabled/
     ```
   - Test and restart Nginx:
     ```
     sudo nginx -t
     sudo systemctl restart nginx
     ```

7. Set up SSL with Let's Encrypt:
   ```
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Monitoring and Maintenance

1. Set up logging:
   - Ensure logs are being written to `/app/logs`
   - Consider using a log rotation tool like `logrotate`

2. Monitor the application:
   - Use tools like Prometheus and Grafana for monitoring
   - Set up alerts for critical errors or performance issues

3. Regular updates:
   - Keep the system and dependencies up to date
   - Regularly pull updates from the repository and rebuild the Docker image

4. Backup:
   - Regularly backup the configuration files and any persistent data

5. Security:
   - Keep the server's OS and all software up to date
   - Use a firewall (e.g., `ufw`) to restrict access
   - Regularly audit the system for security vulnerabilities

Remember to test thoroughly in a staging environment before deploying to production, and always have a rollback plan in case of issues.
