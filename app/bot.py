import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config import Settings
from app.formatter import format_memory_caption
from app.phrase_repository import PhraseRepository
from app.service import MemoryService


logger = logging.getLogger(__name__)

SEND_NEXT_BUTTON = "❤️ Отправить воспоминание"
SEND_RANDOM_BUTTON = "🎲 Случайное фото"


class TravelMemoryBot:
    def __init__(
        self,
        settings: Settings,
        service: MemoryService,
        phrase_repository: PhraseRepository,
    ) -> None:
        self.settings = settings
        self.service = service
        self.phrase_repository = phrase_repository

    def build_application(self) -> Application:
        application = Application.builder().token(self.settings.bot_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_button)
        )

        if application.job_queue is None:
            raise RuntimeError(
                'JobQueue is unavailable. Install dependency "python-telegram-bot[job-queue]".'
            )

        application.job_queue.run_daily(
            self.send_daily_memory,
            time=self.settings.send_time,
            name="daily_travel_memory",
        )

        return application

    def _build_keyboard(self, user_id: int) -> ReplyKeyboardMarkup:
        rows: list[list[KeyboardButton]] = []

        if user_id == self.settings.admin_user_id:
            rows.append([KeyboardButton(SEND_NEXT_BUTTON)])

        rows.append([KeyboardButton(SEND_RANDOM_BUTTON)])

        return ReplyKeyboardMarkup(
            rows,
            resize_keyboard=True,
            is_persistent=True,
        )

    def _is_allowed(self, user_id: int) -> bool:
        return user_id in self.settings.allowed_user_ids

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.effective_message
        if user is None or message is None:
            return

        if not self._is_allowed(user.id):
            logger.warning("Access denied for Telegram user_id=%s", user.id)
            return

        await message.reply_text(
            "Доступ подтверждён ❤️\n"
            "Каждый день здесь будет появляться одно наше совместное воспоминание.",
            reply_markup=self._build_keyboard(user.id),
        )

    async def handle_button(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        user = update.effective_user
        message = update.effective_message
        if user is None or message is None or message.text is None:
            return

        if not self._is_allowed(user.id):
            logger.warning("Access denied for Telegram user_id=%s", user.id)
            return

        if message.text == SEND_RANDOM_BUTTON:
            await self._send_random_memory(
                context=context,
                chat_id=user.id,
            )
            return

        if message.text == SEND_NEXT_BUTTON:
            if user.id != self.settings.admin_user_id:
                await message.reply_text(
                    "Эта кнопка доступна только администратору.",
                    reply_markup=self._build_keyboard(user.id),
                )
                return

            await self._send_next_memory_to_everyone(context)
            return

        await message.reply_text(
            "Используй кнопки под строкой ввода.",
            reply_markup=self._build_keyboard(user.id),
        )

    async def send_daily_memory(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self._send_next_memory_to_everyone(context)

    async def _send_next_memory_to_everyone(
        self,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        try:
            memory = self.service.choose_next()
        except RuntimeError as exc:
            if str(exc) == "All memories have already been sent":
                await self._send_text_to_everyone(
                    context,
                    "❤️ Мы посмотрели все наши воспоминания. Пора создавать новые.",
                )
            else:
                logger.exception("Unable to choose the next memory")
            return

        phrase = self.phrase_repository.get_random_phrase()
        caption = format_memory_caption(memory, phrase)
        successful_sends = 0

        for user_id in self.settings.allowed_user_ids:
            try:
                with memory.photo_path.open("rb") as photo:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                    )
                successful_sends += 1
            except Exception:
                logger.exception("Failed to send memory to user_id=%s", user_id)

        if successful_sends == len(self.settings.allowed_user_ids):
            self.service.confirm_sent(memory)
            logger.info("Memory %s sent to all allowed users", memory.key)
        else:
            logger.warning(
                "Memory %s delivered to %s of %s users; it was not marked as sent",
                memory.key,
                successful_sends,
                len(self.settings.allowed_user_ids),
            )

    async def _send_random_memory(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
    ) -> None:
        try:
            memory = self.service.choose_random()
        except RuntimeError:
            logger.exception("Unable to choose a random memory")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Не нашёл ни одной правильно названной фотографии.",
            )
            return

        phrase = self.phrase_repository.get_random_phrase()
        caption = format_memory_caption(memory, phrase)

        try:
            with memory.photo_path.open("rb") as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                )
        except Exception:
            logger.exception("Failed to send random memory to user_id=%s", chat_id)

    async def _send_text_to_everyone(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
    ) -> None:
        for user_id in self.settings.allowed_user_ids:
            try:
                await context.bot.send_message(chat_id=user_id, text=text)
            except Exception:
                logger.exception("Failed to send text to user_id=%s", user_id)
