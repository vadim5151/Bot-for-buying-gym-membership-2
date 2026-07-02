FROM python:3.14-slim

WORKDIR /tg_bot

ENV PYTHONPATH=/tg_bot
ENV PYTHONUNBUFFERED=1

COPY modules/tg_bot/requirements.txt modules/tg_bot/

RUN pip install --no-cache-dir -r modules/tg_bot/requirements.txt

COPY database/sessions.py database/
COPY database/repositories/user_repository.py database/
COPY database/repositories/price_repository.py database/
COPY database/repositories/notification_reposytory.py database/

COPY configs/logging_config.py configs/
COPY configs/db_config.py configs/
COPY configs/tg_bot_config.py configs/

COPY modules/tg_bot/ modules/tg_bot/


CMD ["python", "-m", "modules.tg_bot.main"]