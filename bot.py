import time
import re
from slackclient import SlackClient

slack_client = SlackClient("xoxb-2525381780-596877194132-JC5Q8zTiD6DCXqSmVfQq2l33")
lunchbot_id = None
path = "favorites.txt"

RTM_READ_DELAY = 1
AVAILABLE_COMMANDS = "list,add,remove"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and event["channel"] == "GHGES5Z08" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == lunchbot_id:
                return message, event["user"]
    return None, None

def parse_direct_mention(message_text):

    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command_string, user):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(AVAILABLE_COMMANDS)

    response = None

    command = command_string.split(" ")[0]

    if command == "list":
        favorites_files = open(path, 'r')
        lines = favorites_files.readlines()

        for line in lines:
            if line.split(':')[0] == user:
                response = "Hi, here's your favorites list: *{}*.".format(line.split(':')[1].strip("\n"))
                break

        if response == None:
            response = "Favorites list not found"

        favorites_files.close()

    elif command == "add":
        favorites_files = open(path, 'r+')
        lines = favorites_files.readlines()

        not_found = True

        for line in lines:
            if line.split(':')[0] == user:
                not_found = False
                lines.remove(line)
                lines.append(user + ":" + command_string.split(" ")[1] + "\n")

                break

            not_found = True

        if not_found:
            lines.append(user + ":" + command_string.split(" ")[1] + "\n")

        favorites_files.seek(0)
        favorites_files.truncate()

        for line in lines:
            favorites_files.write(line)

        favorites_files.close()

        response = "Hi, added *{}* to your favorites".format(command_string.split(" ")[1])

    elif command == "remove":
        favorites_files = open(path, 'r+')
        lines = favorites_files.readlines()

        not_found = True

        for line in lines:
            if line.split(':')[0] == user:
                not_found = False
                lines.remove(line)
                response = "Hi, removed *{}* from your favorites".format(line.split(":")[1].strip("\n"))
                break

            not_found = True

        if not_found:
            response = "Hi, I'm sorry but I couldn't find your favorite list."

        favorites_files.seek(0)
        favorites_files.truncate()

        for line in lines:
            favorites_files.write(line)

        favorites_files.close()

    elif command == "hi" or command == "hello":
        response = "Hello!"

    elif command == "help":
        response = "Available commands are: *{}*.\n\n" \
                   "*list* - Shows the existing favorites list\n" \
                   "*add [item1],[item2]* - Creates a new or replaces the existing favorite list\n" \
                   "*remove* - Removes the whole favorite list".format(AVAILABLE_COMMANDS)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=user,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Lunch bot connected and running!")
        lunchbot_id = slack_client.api_call("auth.test")["user_id"]

        while True:
            command, user = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, user)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed")