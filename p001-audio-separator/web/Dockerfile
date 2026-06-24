# ---- 生产阶段 Dockerfile ----
# Stage 1: Build React SPA
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
# 用 npm install 而非 npm ci，避免跨平台 optional deps 丢失（npm#4828）
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:1.27-alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
