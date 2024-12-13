FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all project files into the image
COPY . .

# Copy the entrypoint script into a known location in the container
COPY docker-entrypoint.sh /usr/local/bin/

# Set the entrypoint to the script
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Expose the port the app runs on
EXPOSE 8080

# Default command to start the application
CMD ["npm", "start"]