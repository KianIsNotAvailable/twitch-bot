import socket
import threading
import random
import mysql.connector
from combinations import combinations
import os

from dotenv import load_dotenv


load_dotenv()
# Twitch IRC configuration
server = 'irc.twitch.tv'
port = 6667
channel = '#kianchatbot'
nickname = 'kianchatbot'
token = os.getenv('MY_OAUTH_TOKEN')


# SQL database configuration
db_config = {
    'host': os.getenv('MY_RDS_ENDPOINT'),
    'user': os.getenv('MY_RDS_USERNAME'),
    'password': os.getenv('MY_RDS_PASSWORD'),
    'database': os.getenv('MY_RDS_DATABASE')
}

print("Bot has started and connected to Twitch IRC!")
# Create a socket connection
irc = socket.socket()
irc.connect((server, port))

# Authenticate with Twitch IRC
irc.send(f'PASS {token}\r\n'.encode('utf-8'))
irc.send(f'NICK {nickname}\r\n'.encode('utf-8'))
irc.send(f'JOIN {channel}\r\n'.encode('utf-8'))

# Connect to MySQL database
db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor(buffered=True)

# Function to execute when a message is received
def on_message(user, msg):
    # Ignore messages from the bot itself
    if user == nickname:
        return

    sender_username = user.split('!')[0]

     # Split the message into words
    words = msg.split()

    # The first word is the command, the rest are arguments
    command_name = words[0].lower()  # Convert to lowercase for case-insensitivity
    args = words[1:]

    # Add users to the database
    cursor.execute('SELECT COUNT(*) AS user_count FROM user_data WHERE username = %s', (sender_username,))
    user_count_row = cursor.fetchone()

    # Check if user_count_row is None
    if user_count_row is None:
        print("No rows found")
        return

    user_count = user_count_row[0]

    # If the user is not in the database, insert them
    if user_count == 0:
        cursor.execute('INSERT INTO user_data (username) VALUES (%s)', (sender_username,))
        db_connection.commit()
        print(f"User {sender_username} added to the database.")


    # Commands
    if command_name == '!gift':
        cursor.execute('SELECT points FROM user_data WHERE username = %s', (sender_username,))
        result = cursor.fetchone()
        print(f"User {sender_username} used command !gift")

        # If their points are 0, they can receive a gift
        balance = result[0] if result else 0
        if balance == 0:
            cursor.execute('UPDATE user_data SET points = points + 1000 WHERE username = %s', (sender_username,))
            db_connection.commit()
            irc.send(f'PRIVMSG {channel} :{sender_username}, you have been gifted 1000 points.\r\n'.encode('utf-8'))
            print(f"* Executed {command_name} command")
        else:
            irc.send(f'PRIVMSG {channel} :{sender_username}, you already had your gift. You can have another when you run out of points\r\n'.encode('utf-8'))

    elif command_name == '!balance':
        cursor.execute('SELECT points FROM user_data WHERE username = %s', (sender_username,))
        result = cursor.fetchone()
        if result:
            irc.send(f'PRIVMSG {channel} :{sender_username}, your balance is {result[0]} points.\r\n'.encode('utf-8'))
        else:
            irc.send(f'PRIVMSG {channel} :{sender_username}, you have no points.\r\n'.encode('utf-8'))

    elif command_name == '!spin':
        points = int(args[0]) if args else 0
        spin(sender_username, points)

    elif command_name == '!odds':
        irc.send(f'PRIVMSG {channel} :Odds: Jebaited = 0.5x Kappa = 1.1x DansGame = 1.5x MaxLOL = 1.7x TriHard = 5x Kreygasm = 10x\r\n'.encode('utf-8'))

    elif command_name == '!reset':
        if not args:
            cursor.execute('UPDATE user_data SET points = 1000 WHERE username = %s', (sender_username,))
            db_connection.commit()

    else:
        irc.send(f'PRIVMSG {channel} :* Unknown command {command_name}\r\n'.encode('utf-8'))

# Function to execute the "spin" command 
def spin(sender_username, points):
    cursor.execute('SELECT points FROM user_data WHERE username = %s', (sender_username,))
    result = cursor.fetchone()

    if not result:
        return

    user_points = result[0]

    if points > user_points:
        irc.send(f'PRIVMSG {channel} :{sender_username}, you do not have enough points for that.\r\n'.encode('utf-8'))
        return

    elif not points or points <= 0:
        irc.send(f'PRIVMSG {channel} :{sender_username}, you can\'t gamble with nothing\r\n'.encode('utf-8'))
        return

    else:
        num = random_index()
        irc.send(f'PRIVMSG {channel} :{sender_username}, you rolled {num}\r\n'.encode('utf-8'))

        if num == "Jebaited Jebaited Jebaited":
            update_points(sender_username, points * 0.5)
        elif num == "Kappa Kappa Kappa":
            update_points(sender_username, points * 1.1)
        elif num == "DansGame DansGame DansGame":
            update_points(sender_username, points * 1.5)
        elif num == "MaxLOL MaxLOL MaxLOL":
            update_points(sender_username, points * 1.7)
        elif num == "TriHard TriHard TriHard":
            update_points(sender_username, points * 5)
        elif num == "Kreygasm Kreygasm Kreygasm":
            update_points(sender_username, points * 10)
        else:
            update_points(sender_username, -points)


# function to update points in the database
def update_points(username, points_change):
    try:
        if cursor:
            cursor.execute('UPDATE user_data SET points = points + %s WHERE username = %s', (points_change, username))
            db_connection.commit()
        else:
            print("Cursor is None")
    except mysql.connector.Error as error:
        print("Error updating points:", error)



# function to generate a random index
def random_index():
    index = random.randint(0, len(combinations) - 1)
    return combinations[index]

# Function to listen for messages
def listen_for_messages():
    while True:
        data = irc.recv(2048).decode('utf-8')
        if data.startswith('PING'):
            irc.send('PONG\r\n'.encode('utf-8'))
        elif 'PRIVMSG' in data:
            user = data.split('!')[0][1:]
            message = ':'.join(data.split(':')[2:])
            threading.Thread(target=on_message, args=(user, message)).start()

# Start a thread to listen for messages
threading.Thread(target=listen_for_messages).start()

# Keep the main thread running
try:
    while True:
        pass
except KeyboardInterrupt:
        
    pass
