from chatbot import Chatbot

bot = Chatbot()

while True:
    user_input = input("You: ")
    reply = bot.respond(user_input)
    print("Bot:", reply)
    if user_input.lower() in ["bye", "exit", "quit"]:
        break
