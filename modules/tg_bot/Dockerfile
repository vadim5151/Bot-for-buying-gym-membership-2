FROM python:3.14-slim

WORKDIR /tg_bot

ENV PYTHONPATH=/tg_bot
ENV PYTHONUNBUFFERED=1

COPY modules/tg_bot/requirements.txt modules/tg_bot/

RUN pip install --no-cache-dir -r modules/tg_bot/requirements.txt

COPY database/ database/

COPY configs/logging_config.py configs/
COPY configs/db_config.py configs/
COPY configs/tg_bot_config.py configs/

COPY modules/tg_bot/ modules/tg_bot/


CMD ["python", "-m", "modules.tg_bot.main"]