FROM rabbitmq:4-management

COPY rabbitmq.conf /etc/rabbitmq
COPY definitions.json /etc/rabbitmq
COPY .env /etc/rabbitmq

RUN cat /etc/rabbitmq/rabbitmq.conf