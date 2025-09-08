# IMPORT LIBRARIES
# ==========================================
# 'os' and 'platform' are used to detect the operating system
# 'turtle' is the library used to create the game's graphics
import os
import platform
import turtle


# SOUND FILE CONFIGURATION
# ==========================================
# Gets the path of the folder where the script is located
base_path = os.path.dirname(os.path.abspath(__file__))

# Paths for sound files used in the game
# Sound when the ball hits a wall or paddle
bounce_sound = os.path.join(base_path, "bounce.wav")
# Sound when a player scores
score_sound = os.path.join(base_path, "258020__kodack__arcade-bleep-sound.wav")

# Detects which operating system is being used
so = platform.system()


# FUNCTION TO PLAY SOUNDS
# ==========================================
def play_sound(sound_file):
    """
    Plays a sound file asynchronously depending on the operating system:
    - Windows: winsound
    - Linux: aplay
    - macOS: afplay
    """
    if so == "Windows":
        import winsound
        winsound.PlaySound(sound_file, winsound.SND_ASYNC)
    elif so == "Linux":
        os.system(f"aplay {sound_file} >/dev/null 2>&1 &")
    elif so == "Darwin":  # macOS
        os.system(f"afplay {sound_file} >/dev/null 2>&1 &")


# GAME WINDOW CONFIGURATION
# ==========================================
# Creates the game window

screen = turtle.Screen()
screen.title("My Pong")  # Window title
screen.bgcolor("black")  # Background color
screen.setup(width=800, height=600)  # Window size
screen.tracer(0)  # Disables automatic screen updates for performance

# CREATE PADDLES
# ==========================================
# Paddle for Player 1 (left side)
paddle_1 = turtle.Turtle()
paddle_1.speed(0)                       # Fastest drawing speed
paddle_1.shape("square")                # Square shape
paddle_1.color("white")                  # White color
paddle_1.shapesize(stretch_wid=5, stretch_len=1)
# Stretch to look like a paddle
paddle_1.penup()                         # Prevents drawing lines
paddle_1.goto(-350, 0)                   # Initial position on the left side

# Paddle for Player 2 (right side)
paddle_2 = turtle.Turtle()
paddle_2.speed(0)
paddle_2.shape("square")
paddle_2.color("white")
paddle_2.shapesize(stretch_wid=5, stretch_len=1)
paddle_2.penup()
paddle_2.goto(350, 0)                    # Initial position on the right side


# CREATE BALL
# ==========================================
ball = turtle.Turtle()
ball.speed(0)
ball.shape("square")
ball.color("white")
ball.penup()
ball.goto(0, 0)      # Starts in the center
ball.dx = 5          # Horizontal speed
ball.dy = 5          # Vertical speed


# SCORE SYSTEM
# ==========================================
score_1 = 0  # Player 1 score
score_2 = 0  # Player 2 score


# HUD (SCORE DISPLAY)
# ==========================================
hud = turtle.Turtle()
hud.speed(0)
hud.shape("square")
hud.color("white")
hud.penup()
hud.hideturtle()                      # Hide the turtle cursor
hud.goto(0, 260)                       # Score position
hud.write("0 : 0", align="center", font=("Press Start 2P", 24, "normal"))


# VICTORY MESSAGE
# ==========================================
msg = turtle.Turtle()
msg.speed(0)
msg.shape("square")
msg.color("white")
msg.penup()
msg.hideturtle()


# PLAYER LABELS
# ==========================================
player_label = turtle.Turtle()
player_label.speed(0)
player_label.color("white")
player_label.penup()
player_label.hideturtle()
player_label.goto(-200, 260)  # Text for Player 1
(player_label.write("Player 1", align="center",
 font=("Press Start 2P", 14, "normal")))
player_label.goto(200, 260)   # Text for Player 2
(player_label.write("Player 2", align="center",
 font=("Press Start 2P", 14, "normal")))


# GAME STATE VARIABLES
# ==========================================
PADDLE_STEP = 12  # Speed of paddle movement
p1_up_pressed = False     # Player 1 pressed "W"
p1_down_pressed = False   # Player 1 pressed "S"
p2_up_pressed = False     # Player 2 pressed Up Arrow
p2_down_pressed = False   # Player 2 pressed Down Arrow

game_over = False         # Indicates if the game has ended


# FUNCTIONS TO DETECT KEY PRESSES
# ==========================================
# Player 1
def press_w():
    global p1_up_pressed
    p1_up_pressed = True


def press_s():
    global p1_down_pressed
    p1_down_pressed = True

# Player 2 (Arrow keys)


def press_up():
    global p2_up_pressed
    p2_up_pressed = True


def press_down():
    global p2_down_pressed
    p2_down_pressed = True


# FUNCTIONS TO DETECT KEY RELEASES

def release_w():
    global p1_up_pressed
    p1_up_pressed = False


def release_s():
    global p1_down_pressed
    p1_down_pressed = False


def release_up():
    global p2_up_pressed
    p2_up_pressed = False


def release_down():
    global p2_down_pressed
    p2_down_pressed = False


# FUNCTION TO RESTART THE GAME
# ==========================================
def restart_game():
    """
    Restarts the game by:
    - Resetting scores
    - Resetting ball position
    - Clearing victory message
    """
    global score_1, score_2, game_over
    score_1 = 0
    score_2 = 0
    game_over = False
    hud.clear()
    hud.write(
     "0 : 0", align="center",
     font=("Press Start 2P", 24, "normal")
    )
    msg.clear()
    ball.goto(0, 0)
    ball.dx = 5
    ball.dy = 5
    game_loop()  # Restart the main loop


# FUNCTION TO QUIT THE GAME
# ==========================================
def quit_game():
    """Closes the game window and exits the program."""
    screen.bye()


# CLAMP FUNCTION
# ==========================================
def clamp(v, lo, hi):
    """
    Ensures the value 'v' stays within the range [lo, hi].
    Useful to keep paddles inside the screen boundaries.
    """
    return max(lo, min(hi, v))


# KEY BINDINGS
# ==========================================
screen.listen()  # Enables key detection

# Player 1
screen.onkeypress(press_w, "w")
screen.onkeypress(press_s, "s")
screen.onkeyrelease(release_w, "w")
screen.onkeyrelease(release_s, "s")

# Player 2
screen.onkeypress(press_up, "Up")
screen.onkeypress(press_down, "Down")
screen.onkeyrelease(release_up, "Up")
screen.onkeyrelease(release_down, "Down")

# Restart (R) and Quit (Q)
screen.onkeypress(restart_game, "r")
screen.onkeypress(quit_game, "q")


# MAIN GAME LOOP
# ==========================================
def game_loop():
    """
    Main game function:
    - Updates screen
    - Moves paddles and ball
    - Detects collisions
    - Updates score
    - Checks for victory
    """
    global score_1, score_2, game_over

    screen.update()  # Refresh the screen

    # Stop everything if the game is over
    if game_over:
        return

    # --- Victory condition ---
    if score_1 >= 10 or score_2 >= 10:
        msg.clear()
        msg.goto(0, 50)
        winner = "Player 1" if score_1 >= 10 else "Player 2"
        msg.write(
            f"{winner} Wins!\nPress R to Restart or Q to Quit",
            align="center",
            font=("Press Start 2P", 18, "normal"),
        )
        game_over = True
        return

    # --- Paddle movement ---
    if p1_up_pressed:
        paddle_1.sety(clamp(paddle_1.ycor() + PADDLE_STEP, -250, 250))
    if p1_down_pressed:
        paddle_1.sety(clamp(paddle_1.ycor() - PADDLE_STEP, -250, 250))
    if p2_up_pressed:
        paddle_2.sety(clamp(paddle_2.ycor() + PADDLE_STEP, -250, 250))
    if p2_down_pressed:
        paddle_2.sety(clamp(paddle_2.ycor() - PADDLE_STEP, -250, 250))

    # --- Ball movement ---
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # --- Ball collision with top and bottom walls ---
    if ball.ycor() > 290:
        play_sound(bounce_sound)
        ball.sety(290)
        ball.dy *= -1  # Reverse vertical direction

    if ball.ycor() < -290:
        play_sound(bounce_sound)
        ball.sety(-290)
        ball.dy *= -1

    # --- Ball goes out on the left side (Player 2 scores) ---
    if ball.xcor() < -390:
        score_2 += 1
        hud.clear()
        (hud.write(f"{score_1} : {score_2}", align="center",
         font=("Press Start 2P", 24, "normal")))
        play_sound(score_sound)
        ball.goto(0, 0)
        ball.dx = -5
        ball.dy = 5

    # Ball goes out on the right side (Player 1 scores)
    if ball.xcor() > 390:
        score_1 += 1
        hud.clear()
        (hud.write(f"{score_1} : {score_2}", align="center",
         font=("Press Start 2P", 24, "normal")))
        play_sound(score_sound)
        ball.goto(0, 0)
        ball.dx = 5
        ball.dy = 5

    # --- Ball collision with left paddle ---

    if (
        ball.xcor() < -330 and paddle_1.ycor() + 50 >
        ball.ycor() > paddle_1.ycor() - 50
    ):
        play_sound(bounce_sound)
        ball.setx(-330)
        offset = (ball.ycor() - paddle_1.ycor()) / 50.0  # Adjust bounce angle
        ball.dx *= -1.1  # Increase speed and reverse direction
        ball.dy = offset * abs(ball.dx)

    # --- Ball collision with right paddle ---
    if (
        ball.xcor() > 330 and paddle_2.ycor() + 50 >
        ball.ycor() > paddle_2.ycor() - 50
    ):
        play_sound(bounce_sound)
        ball.setx(330)
        offset = (ball.ycor() - paddle_2.ycor()) / 50.0  # Adjust bounce angle
        ball.dx *= -1.1  # Increase speed and reverse direction
        ball.dy = offset * abs(ball.dx)

    # Small delay to control game speed
    turtle.time.sleep(0.01)

    # Call the game loop again every 20ms
    screen.ontimer(game_loop, 20)


# START THE GAME
# ==========================================
game_loop()
screen.mainloop()
