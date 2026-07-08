FROM docker.m.daocloud.io/node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 40003

CMD ["npm", "run", "dev"]
