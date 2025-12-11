import asyncio
import logging
from bot.bot import dp, bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Error in bot")
if __name__ == '__main__':
    asyncio.run(main())