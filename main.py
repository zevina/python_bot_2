# выполнено совместно с Рябовым Андреем

import logging
import emoji
import token_bot
import random

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

TOKEN = token_bot.TOKEN
reply_keyboard = [['/play', '/settings'],
                  ['/rules', '/close']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

candies = 100
step = 28


def start(update, context):
    name = f"{update.message.from_user.first_name} {update.message.from_user.last_name}"
    update.message.reply_text(emoji.emojize(
        f"Привет, {name}!\nЯ бот для игры в конфетки. Поиграем?"
        f"\n\n/play            :video_game:  играть"
        f"\n/settings     :gear:  настройки игры"
        f"\n/rules          :scroll:  правила игры"
        f"\n/close          :cross_mark:  закрыть"),
        reply_markup=markup
    )


def close_keyboard(update, context):
    update.message.reply_text(emoji.emojize(
        "Ну ок :face_with_rolling_eyes:"),
        reply_markup=ReplyKeyboardRemove()
    )


def settings(update, context):
    update.message.reply_text(
        "Введите количество конфет на кону и сколько конфет можно забрать за 1 ход:")
    return 1


def set_settings(update, context):
    global candies
    global step
    candies, step = map(int, update.message.text.split())
    update.message.reply_text(
        "Правила установлены. Начинай игру!")
    return ConversationHandler.END


def rules(update, context):
    update.message.reply_text(emoji.emojize(
        "На столе лежат конфеты."
        "\nИграют два игрока делая ход друг после друга. "
        "\nВсе конфеты оппонента достаются сделавшему последний ход, он и будет победителем."
        "\n\nПеред началом игры необходимо определить общее количество конфет на столе и сколько конфет можно забрать за 1 ход.  "
        "\n :gear:  /settings"
        "\n\n Удачи!"))


def play(update, context):
    update.message.reply_text(emoji.emojize(f'На столе {candies} конфет :candy:'
                                            f'\nБрать можно не больше {step} конфет!'),
                              reply_markup=ReplyKeyboardRemove())
    return 1


def play_step(update, context):
    global candies
    try:
        x = int(update.message.text)
        if 0 < x <= step:
            candies -= x
            if candies <= step:
                update.message.reply_text(emoji.emojize("Игра окончена, бот победил! :squinting_face_with_tongue:"),
                                          reply_markup=markup)
                return ConversationHandler.END
            else:
                update.message.reply_text(emoji.emojize(f'На столе {candies} конфет :candy:'))
                y = candies % (step + 1)
                if y > 0:
                    update.message.reply_text(f'Я беру {y} конфет!')
                    candies -= y
                    update.message.reply_text(emoji.emojize(f'Осталось {candies} конфет :candy:'))
                    if candies <= step:
                        update.message.reply_text(emoji.emojize("Игра окончена, ты победил/а!"), reply_markup=markup)
                        return ConversationHandler.END
                else:
                    y = random.randint(1, step)
                    update.message.reply_text(f'Я беру {y} конфет!')
                    candies -= y
                    update.message.reply_text(emoji.emojize(f'Осталось {candies} конфет :candy:'))
                    if candies <= step:
                        update.message.reply_text(
                            emoji.emojize("Игра окончена, ты победил/а! :clapping_hands_light_skin_tone:"),
                            reply_markup=markup)
                        return ConversationHandler.END
        else:
            update.message.reply_text(emoji.emojize(f":warning: Введите положительное число, которое не больше {step}"))
    except Exception:
        update.message.reply_text(emoji.emojize(":warning: Введите корректное значение"))


def stop(update, context):
    update.message.reply_text("Спасибо за игру!")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    settings_handler = ConversationHandler(

        entry_points=[CommandHandler('settings', settings)],

        states={
            1: [MessageHandler(Filters.text & ~Filters.command, set_settings)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    play_handler = ConversationHandler(

        entry_points=[CommandHandler('play', play)],

        states={
            1: [MessageHandler(Filters.text & ~Filters.command, play_step)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(play_handler)
    dp.add_handler(settings_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("rules", rules))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
