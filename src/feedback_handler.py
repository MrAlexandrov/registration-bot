from state_handler import StateHandler
from feedback_storage import feedback_storage
from constants import *

class FeedbackHandler:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.state_handler = StateHandler(user_storage)
        self.feedback_storage = feedback_storage

    async def handle_command(self, update, context):
        user_id = update.message.from_user.id
        command = update.message.text

        if command == CREATE_SURVEY:
            await self.state_handler.transition_state(update, context, CREATE_SURVEY_NAME)
        elif command == SEND_SURVEY:
            surveys = self.feedback_storage.get_all_surveys()
            if not surveys:
                await context.bot.send_message(chat_id=user_id, text="Пока не создано ни одного опроса.")
                return

            keyboard = [[f"{s[1]} (id: {s[0]})"] for s in surveys]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text="Выбери опрос для отправки:", reply_markup=reply_markup)
            await self.state_handler.transition_state(update, context, ADMIN_SELECT_SURVEY_TO_SEND)
        elif command == VIEW_RESULTS:
            surveys = self.feedback_storage.get_all_surveys()
            if not surveys:
                await context.bot.send_message(chat_id=user_id, text="Пока не создано ни одного опроса.")
                return
            
            keyboard = [[f"{s[1]} (id: {s[0]})"] for s in surveys]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text="Выбери опрос для просмотра результатов:", reply_markup=reply_markup)
            await self.state_handler.transition_state(update, context, ADMIN_VIEW_SURVEY_RESULTS)


    async def handle_input(self, update, context):
        user_id = update.message.from_user.id
        user_data = self.user_storage.get_user(user_id)
        current_state = user_data.get('state')
        text = update.message.text

        if current_state == CREATE_SURVEY_NAME:
            survey_id = self.feedback_storage.create_survey(text)
            context.user_data['current_survey_id'] = survey_id
            await self.state_handler.transition_state(update, context, CREATE_SURVEY_ADD_QUESTION)

        elif current_state == CREATE_SURVEY_ADD_QUESTION:
            if text == ADD_QUESTION:
                await self.state_handler.transition_state(update, context, CREATE_SURVEY_QUESTION_TEXT)
            elif text == FINISH_SURVEY_CREATION:
                await context.bot.send_message(chat_id=user_id, text="Опрос успешно создан!")
                await self.state_handler.transition_state(update, context, REGISTERED) # Or some admin menu

        elif current_state == CREATE_SURVEY_QUESTION_TEXT:
            context.user_data['new_question_text'] = text
            await self.state_handler.transition_state(update, context, CREATE_SURVEY_QUESTION_TYPE)

        elif current_state == CREATE_SURVEY_QUESTION_OPTIONS:
            survey_id = context.user_data.get('current_survey_id')
            question_text = context.user_data.get('new_question_text')
            question_type = context.user_data.get('new_question_type')
            options = [opt.strip() for opt in text.split(',')]
            
            self.feedback_storage.add_question_to_survey(survey_id, question_text, question_type, options)
            await self.state_handler.transition_state(update, context, CREATE_SURVEY_ADD_QUESTION)

        elif current_state == ADMIN_SELECT_SURVEY_TO_SEND:
            if text == SEND_TO_ALL:
                survey_id = context.user_data.get('survey_to_send_id')
                survey_name = context.user_data.get('survey_to_send_name')
                self.send_survey_to_users(context, survey_id, survey_name, self.user_storage.get_all_users())
                await self.state_handler.transition_state(update, context, REGISTERED)
            elif text == SEND_TO_FILTERED:
                await self.state_handler.transition_state(update, context, ADMIN_FILTER_USERS)
            else:
                try:
                    survey_name, survey_id_str = text.rsplit(' (id: ', 1)
                    survey_id = int(survey_id_str[:-1])
                    context.user_data['survey_to_send_id'] = survey_id
                    context.user_data['survey_to_send_name'] = survey_name
                    await self.state_handler.transition_state(update, context, ADMIN_FILTER_USERS)
                except (ValueError, IndexError):
                    await context.bot.send_message(chat_id=user_id, text="Неверный формат. Пожалуйста, выбери опрос из списка.")
                    return

        elif current_state == ADMIN_FILTER_USERS:
            filters = text.split(',')
            user_sets = []

            for f in filters:
                f = f.strip()
                if not f: continue
                
                try:
                    key, value = f.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if key.startswith('q'):
                        question_id = int(key[1:])
                        user_sets.append(set(self.feedback_storage.find_users_by_answer(question_id, value)))
                    elif key == 'name':
                        user_sets.append(set(self.user_storage.find_users_by_name(value)))
                    elif key == 'telegram_id':
                         user_sets.append({int(value)})
                except ValueError:
                    await context.bot.send_message(chat_id=user_id, text=f"Неверный формат фильтра: {f}")
                    return
            
            if not user_sets:
                await context.bot.send_message(chat_id=user_id, text="Вы не ввели ни одного фильтра.")
                return

            # Intersect all sets to get users that match all criteria
            final_users = user_sets[0]
            for i in range(1, len(user_sets)):
                final_users.intersection_update(user_sets[i])

            survey_id = context.user_data.get('survey_to_send_id')
            survey_name = context.user_data.get('survey_to_send_name')
            await self.send_survey_to_users(context, survey_id, survey_name, list(final_users))
            await self.state_handler.transition_state(update, context, REGISTERED)

        elif current_state == ADMIN_VIEW_SURVEY_RESULTS:
            try:
                survey_name, survey_id_str = text.rsplit(' (id: ', 1)
                survey_id = int(survey_id_str[:-1])
            except (ValueError, IndexError):
                await context.bot.send_message(chat_id=user_id, text="Неверный формат. Пожалуйста, выбери опрос из списка.")
                return
            
            results = self.feedback_storage.get_survey_results(survey_id)
            if not results:
                await context.bot.send_message(chat_id=user_id, text="По этому опросу пока нет ответов.")
                await self.state_handler.transition_state(update, context, REGISTERED)
                return

            report = f"Результаты опроса '{survey_name}':\n\n"
            current_user = None
            for question_text, answer_text, user_name in results:
                if user_name != current_user:
                    report += f"\n--- {user_name} ---\n"
                    current_user = user_name
                report += f"❓ {question_text}\n💬 {answer_text}\n"

            # Split message if it's too long for Telegram
            if len(report) > 4096:
                for x in range(0, len(report), 4096):
                    await context.bot.send_message(chat_id=user_id, text=report[x:x+4096])
            else:
                await context.bot.send_message(chat_id=user_id, text=report)
            
            await self.state_handler.transition_state(update, context, REGISTERED)

    async def send_survey_to_users(self, context, survey_id, survey_name, user_ids):
        questions = self.feedback_storage.get_survey_questions(survey_id)
        if not user_ids:
            await context.bot.send_message(chat_id=context._user_id, text="Не найдено пользователей по вашему запросу.")
            return

        for user_id in user_ids:
            if questions:
                first_question = questions[0]
                keyboard = self.create_question_keyboard(first_question)
                try:
                    await context.bot.send_message(chat_id=user_id, text=first_question['text'], reply_markup=keyboard)
                    self.feedback_storage.log_survey_send(survey_id, user_id, status="in_progress")
                except Exception as e:
                    logger.error(f"Failed to send message to {user_id}: {e}")
        
        await context.bot.send_message(chat_id=context._user_id, text=f"Опрос '{survey_name}' отправлен {len(user_ids)} пользователям.")


    def create_question_keyboard(self, question):
        q_type = question['question_type']
        q_id = question['id']
        
        if q_type == Q_TEXT_INPUT:
            return None # No keyboard for text input

        buttons = []
        if q_type in [Q_SINGLE_CHOICE, Q_MULTIPLE_CHOICE]:
            for option in question['options']:
                callback_data = f"answer|{q_id}|{option}"
                buttons.append([InlineKeyboardButton(option, callback_data=callback_data)])
        
        if q_type == Q_MULTIPLE_CHOICE:
            buttons.append([InlineKeyboardButton("Готово", callback_data=f"answer|{q_id}|done")])

        return InlineKeyboardMarkup(buttons) if buttons else None

    async def handle_inline_query(self, update, context):
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        user_data = self.user_storage.get_user(user_id)
        current_state = user_data.get('state')
        
        parts = query.data.split('|')
        action = parts[0]

        if action == 'answer':
            question_id = int(parts[1])
            answer = parts[2]

            # TODO: Handle multiple choice answers (accumulate and save on 'done')
            self.feedback_storage.save_answer(user_id, question_id, answer)
            
            question_details = self.feedback_storage.get_question_details(question_id)
            if not question_details:
                return

            survey_id = question_details['survey_id']
            all_questions = self.feedback_storage.get_survey_questions(survey_id)
            
            current_question_index = -1
            for i, q in enumerate(all_questions):
                if q['id'] == question_id:
                    current_question_index = i
                    break
            
            await query.edit_message_text(text=f"{query.message.text}\n\nВаш ответ: {answer}")

            if current_question_index < len(all_questions) - 1:
                next_question = all_questions[current_question_index + 1]
                keyboard = self.create_question_keyboard(next_question)
                await context.bot.send_message(chat_id=user_id, text=next_question['text'], reply_markup=keyboard)
            else:
                await context.bot.send_message(chat_id=user_id, text="Спасибо, опрос завершен!")
                # TODO: Update survey_sends status to 'completed'

        elif current_state in admin_states and action == 'select':
            value = parts[1]
            if value == SINGLE_CHOICE:
                question_type = Q_SINGLE_CHOICE
            elif value == MULTIPLE_CHOICE:
                question_type = Q_MULTIPLE_CHOICE
            else: # TEXT_INPUT
                question_type = Q_TEXT_INPUT

            context.user_data['new_question_type'] = question_type
            
            if question_type == Q_TEXT_INPUT:
                survey_id = context.user_data.get('current_survey_id')
                question_text = context.user_data.get('new_question_text')
                self.feedback_storage.add_question_to_survey(survey_id, question_text, question_type)
                await self.state_handler.transition_state(update, context, CREATE_SURVEY_ADD_QUESTION)
            else:
                await self.state_handler.transition_state(update, context, CREATE_SURVEY_QUESTION_OPTIONS)