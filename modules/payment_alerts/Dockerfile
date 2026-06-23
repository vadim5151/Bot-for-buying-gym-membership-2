FROM python:3.14-slim

WORKDIR /payment_alerts

ENV PYTHONPATH=/payment_alerts
ENV PYTHONUNBUFFERED=1

COPY modules/payment_alerts/requirements.txt modules/payment_alerts/

RUN pip install --no-cache-dir -r modules/payment_alerts/requirements.txt

COPY configs/tg_bot_config.py configs/
COPY configs/logging_config.py configs/
COPY configs/db_config.py configs/

COPY modules/payment_alerts/ modules/payment_alerts/


CMD ["python", "-m", "modules.payment_alerts.main"]