FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Set environment variable defaults
ENV NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV PORT=3000

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
