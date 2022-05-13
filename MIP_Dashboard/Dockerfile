FROM node:latest

WORKDIR /app

COPY package.json ./

RUN npm install

COPY . .

#RUN npm run build

RUN chown -R node.node /app/node_modules

RUN chmod -R 777 /app

EXPOSE 8080

CMD ["npm", "start"]






# FROM registry.cirrus.ibm.com/ubi8/nodejs-16:latest

# USER root
# RUN dnf install -y python3
# RUN mkdir /home/vcap && ln -s /opt/app-root/src /home/vcap/app && chown -R default:root /home/vcap
# COPY . /tmp
# COPY . /opt/app-root/src
# RUN chmod -R 777 /opt/app-root
# RUN chown -R 1001:0 /tmp
# USER 1001
# #RUN /usr/libexec/s2i/assemble
# RUN npm install
# CMD /usr/libexec/s2i/run