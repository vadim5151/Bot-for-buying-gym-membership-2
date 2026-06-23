FROM python:3.14-slim

WORKDIR /tracking_payment_ends

ENV PYTHONPATH=/tracking_payment_ends
ENV PYTHONUNBUFFERED=1

COPY modules/tracking_payment_ends/requirements.txt modules/tracking_payment_ends/

RUN pip install --no-cache-dir -r modules/tracking_payment_ends/requirements.txt

COPY database/ database/

COPY configs/alerts_config.py configs/
COPY configs/logging_config.py configs/
COPY configs/db_config.py configs/

COPY modules/tracking_payment_ends/ modules/tracking_payment_ends/


CMD ["python", "-m", "modules.tracking_payment_ends.main"]