import logging

from app.bot import TravelMemoryBot
from app.config import load_settings
from app.phrase_repository import PhraseRepository
from app.repository import MemoryRepository
from app.service import MemoryService


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    settings = load_settings()

    repository = MemoryRepository(
        photos_dir=settings.photos_dir,
        database_file=settings.database_file,
    )
    repository.initialize()

    service = MemoryService(repository)
    phrase_repository = PhraseRepository(settings.phrases_file)
    bot = TravelMemoryBot(settings=settings, service=service, phrase_repository=phrase_repository)
    application = bot.build_application()

    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
