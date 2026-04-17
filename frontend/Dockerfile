# Stage 1 – build the Vue app
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json vite.config.js .env.production ./
COPY src ./src
COPY public ./public
COPY index.html ./
RUN npm install && npm run build

# Stage 2 – serve with nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Expose default nginx port
EXPOSE 80
CMD ["nginx", "-g", "daemon off;" ]
