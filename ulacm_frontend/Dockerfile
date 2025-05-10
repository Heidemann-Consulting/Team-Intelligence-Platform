# File: ulacm_frontend/Dockerfile
# Purpose: Builds the Docker image for the React frontend application.
# Uses a multi-stage build for optimized production image size.

# --- Build Stage ---
# Use a Node.js base image for building the React app
FROM node:18-alpine as build-stage

# Set the working directory
WORKDIR /app

# Copy package.json and lock file
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./

# Install dependencies based on the lock file found
# Using yarn as an example, adjust if using npm or pnpm
RUN if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install --frozen-lockfile; \
    else echo "Lockfile not found." && exit 1; \
    fi

# Copy the rest of the application code
COPY . .

# Set build-time environment variables if needed
# ARG VITE_API_BASE_URL=/api/v1
# ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build the React application for production
# The build script is defined in package.json ("build": "tsc && vite build")
# RUN yarn build # Or npm run build / pnpm build
RUN npm run build

# --- Production Stage ---
# Use a lightweight Nginx image to serve the static files
FROM nginx:1.25-alpine as production-stage

# Copy the built static files from the build stage to Nginx's web root directory
COPY --from=build-stage /app/build /usr/share/nginx/html

# This default config should work for most SPAs, serving index.html for any unknown path.
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Example nginx.conf for SPAs:
# server {
#   listen 80;
#   server_name localhost;
#
#   root /usr/share/nginx/html;
#   index index.html index.htm;
#
#   location / {
#     try_files $uri $uri/ /index.html;
#   }
#
#   # Optional: Proxy API requests if Nginx handles both frontend and backend routing
#   # location /api/ {
#   #   proxy_pass http://backend:8000/api/; # Assuming 'backend' is the service name in docker-compose
#   #   proxy_set_header Host $host;
#   #   proxy_set_header X-Real-IP $remote_addr;
#   #   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#   #   proxy_set_header X-Forwarded-Proto $scheme;
#   # }
# }

# Expose port 80 (default Nginx port)
EXPOSE 80

# Default command to start Nginx
CMD ["nginx", "-g", "daemon off;"]
