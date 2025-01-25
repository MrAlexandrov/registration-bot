import re
from telegram import Update
from telegram.constants import ParseMode
from typing import Optional, List


class MessageFormatter:
    """Класс для обработки форматированного текста Telegram (MarkdownV2 и HTML)."""

    @staticmethod
    def _escape_markdown_v2(text: str) -> str:
        """Экранирует специальные символы в MarkdownV2."""
        return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

    @staticmethod
    def _escape_html(text: str) -> str:
        """Экранирует специальные символы в HTML."""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    @staticmethod
    def _apply_entities_to_text(text: str, entities: List, mode: str) -> str:
        """Применяет форматирование к тексту (MarkdownV2 или HTML)."""

        if not entities:
            return (
                MessageFormatter._escape_markdown_v2(text)
                if mode == ParseMode.MARKDOWN_V2
                else MessageFormatter._escape_html(text)
            )

        result = ""
        offset = 0

        for entity in entities:
            # Добавляем неформатированный текст перед entity
            if entity.offset > offset:
                non_entity_text = text[offset:entity.offset]
                escaped_text = (
                    MessageFormatter._escape_markdown_v2(non_entity_text)
                    if mode == ParseMode.MARKDOWN_V2
                    else MessageFormatter._escape_html(non_entity_text)
                )
                result += escaped_text

            entity_text = text[entity.offset : entity.offset + entity.length]
            escaped_text = (
                MessageFormatter._escape_markdown_v2(entity_text)
                if mode == ParseMode.MARKDOWN_V2
                else MessageFormatter._escape_html(entity_text)
            )

            # Выбираем форматирование для Markdown или HTML
            if mode == ParseMode.MARKDOWN_V2:
                formatting = {
                    "bold": f"*{escaped_text}*",
                    "italic": f"_{escaped_text}_",
                    "underline": f"__{escaped_text}__",
                    "strikethrough": f"~{escaped_text}~",
                    "code": f"`{escaped_text}`",
                    "pre": f"```{escaped_text}```",
                    "text_link": f"[{escaped_text}]({MessageFormatter._escape_markdown_v2(entity.url)})"
                    if entity.url
                    else escaped_text,
                }
            else:  # HTML Mode
                formatting = {
                    "bold": f"<b>{escaped_text}</b>",
                    "italic": f"<i>{escaped_text}</i>",
                    "underline": f"<u>{escaped_text}</u>",
                    "strikethrough": f"<s>{escaped_text}</s>",
                    "code": f"<code>{escaped_text}</code>",
                    "pre": f"<pre>{escaped_text}</pre>",
                    "text_link": f'<a href="{entity.url}">{escaped_text}</a>'
                    if entity.url
                    else escaped_text,
                }

            # Применяем форматирование
            result += formatting.get(entity.type, escaped_text)
            offset = entity.offset + entity.length

        # Добавляем оставшийся текст
        if offset < len(text):
            remaining_text = text[offset:]
            escaped_text = (
                MessageFormatter._escape_markdown_v2(remaining_text)
                if mode == ParseMode.MARKDOWN_V2
                else MessageFormatter._escape_html(remaining_text)
            )
            result += escaped_text

        return result

    @staticmethod
    def get_escaped_text(message: Optional[Update], parse_mode: str = ParseMode.MARKDOWN_V2) -> str:
        """Возвращает текст с учётом форматирования (MarkdownV2 или HTML)."""

        print(f"message = {message}")

        if not message or not message.text:
            return ""

        return MessageFormatter._apply_entities_to_text(
            message.text, message.entities or [], parse_mode
        )