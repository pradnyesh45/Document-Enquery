# Build stage
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose port (adjust if your React app uses a different port)
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
