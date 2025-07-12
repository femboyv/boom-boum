import pygame
import json

pygame.init()
pygame.joystick.init()


screen = pygame.display.set_mode((960, 540), vsync=1, display=0)
screen_caca = pygame.display.set_mode((960, 540), vsync=1, display=1)
MIDDLE_SCREEN = (screen.get_width() / 2, screen.get_height() / 2)
clock = pygame.time.Clock()
running = True
fps = 100


## palette ##


def load_palette() -> list:
    def dict_to_color(color_dict: dict):
        return pygame.Color(
            color_dict["r"], color_dict["g"], color_dict["b"], color_dict["a"]
        )

    with open("palette.txt", "r") as file:
        string_in_file = file.read()
        palette_list_dict = json.loads(string_in_file)
        palette_list_color = []

        for color_dict in palette_list_dict:
            palette_list_color.append(dict_to_color(color_dict))
        return palette_list_color


PALETTE = load_palette()

WHITE = PALETTE[0]
GRAY = PALETTE[1]
BLUE = PALETTE[2]
BLACK = PALETTE[3]


## manette ##
class manette_class:
    def __init__(self, id, dead_zone_radius):
        self.joysitck = pygame.joystick.Joystick(id)
        self.joysitck.init()
        print(self.joysitck.get_name(), "connected")

        self.movement_axis = pygame.Vector2(0, 0)
        self.camera_axis = pygame.Vector2(0, 0)

        self.buttons_pressed = []
        self.key_map = {
            0: "A Button",
            1: "B Button",
            2: "X Button",
            3: "Y Button",
            4: "- Button",
            5: "Home Button",
            6: "+ Button",
            7: "L. Stick In",
            8: "R. Stick In",
            9: "Left Bumper",
            10: "Right Bumper",
            11: "D-pad Up",
            12: "D-pad Down",
            13: "D-pad Left",
            14: "D-pad Right",
            15: "Capture Button",
            16: "Left Trigger",
            17: "Right Trigger",
        }

        self.dead_zone_radius = dead_zone_radius

    def step(self):

        ## movmement axis ##
        self.movement_axis = pygame.Vector2(
            self.joysitck.get_axis(0), self.joysitck.get_axis(1)
        )
        if self.movement_axis.length() < self.dead_zone_radius:
            self.movement_axis = pygame.Vector2(0, 0)

        elif self.movement_axis.length() > 1:
            self.movement_axis = self.movement_axis.normalize()

        ## camera axis ##
        self.camera_axis = pygame.Vector2(
            self.joysitck.get_axis(2), self.joysitck.get_axis(3)
        )
        if self.camera_axis.length() < self.dead_zone_radius:
            self.camera_axis = pygame.Vector2(0, 0)

        elif self.camera_axis.length() > 1:
            self.camera_axis = self.camera_axis.normalize()

        ## key ##
        self.buttons_pressed = []
        for button_number in range(16):  ## number of button + 1 for the 0 at start
            if self.joysitck.get_button(button_number):
                self.buttons_pressed.append(self.key_map[button_number])
        # trigger are not button but axis
        # axis is at 0 at start, pressed it's a little bit less than 1 and released at -1
        print(self.joysitck.get_axis(4))
        if self.joysitck.get_axis(4) > 0:  # left trigger
            self.buttons_pressed.append(self.key_map[16])

        if self.joysitck.get_axis(5) > 0:  # right trigger
            self.buttons_pressed.append(self.key_map[17])


manette = manette_class(0, 0.3)


## player ##


class player_class:
    def __init__(
        self,
        x: int,
        y: int,
        direction: int,
        is_controlled_by_manette: bool,
        sprite: pygame.Surface,
        cannon_sprite: pygame.Surface,
        speed_per_sec: int,
        cannon_speed_turn: float,
        sprite_speed_turn: float,
    ):
        self.x = x
        self.y = y

        self.sprite = sprite  # the spaceship
        self.cannon_sprite = cannon_sprite

        self.direction = pygame.Vector2.from_polar((1, direction))
        self.direction: pygame.Vector2
        self.sprite_angle = self.direction.copy()

        self.direction_cannon = self.direction.copy()
        self.cannon_sprite_angle = self.direction.copy()

        self.is_controlled_by_manette = is_controlled_by_manette

        self.max_speed = speed_per_sec / fps

        self.cannon_speed_turn = cannon_speed_turn
        self.sprite_speed_turn = sprite_speed_turn

        self.key_map = {
            "A Button": "nothing",
            "B Button": "nothing",
            "X Button": "nothing",
            "Y Button": "nothing",
            "- Button": "nothing",
            "Home Button": "nothing",
            "+ Button": "nothing",
            "L. Stick In": "nothing",
            "R. Stick In": "nothing",
            "Left Bumper": "nothing",
            "Right Bumper": "nothing",
            "D-pad Up": "nothing",
            "D-pad Down": "nothing",
            "D-pad Left": "nothing",
            "D-pad Right": "nothing",
            "Capture Button": "nothing",
            "Left Trigger": "move",
            "Right Trigger": "nothing",
        }

    def draw_spaceship(self, image_angle: pygame.Vector2):
        rotated_sprite = pygame.transform.rotate(
            self.sprite, -image_angle.as_polar()[1] - 90
        )

        rect_sprite_rotated = rotated_sprite.get_rect(center=(self.x, self.y))
        screen.blit(rotated_sprite, rect_sprite_rotated)

    def draw_cannon(self, image_angle: pygame.Vector2):

        rotated_cannon_sprite = pygame.transform.rotate(
            self.cannon_sprite, -image_angle.as_polar()[1] - 90
        )

        rect_cannon_sprite_rotated = rotated_cannon_sprite.get_rect(
            center=(self.x, self.y)
        )

        screen.blit(
            rotated_cannon_sprite,
            rect_cannon_sprite_rotated,
        )

    def turning(
        self,
        vector_to_turn_toward: pygame.Vector2,
        vector_turning: pygame.Vector2,
        speed: float,
    ):
        if vector_to_turn_toward != pygame.Vector2(0, 0):
            vector_turning.move_towards_ip(vector_to_turn_toward, speed)
            vector_turning.normalize_ip()

    def move(self, speed: pygame.Vector2):
        self.x += speed.x
        self.y += speed.y

    def handle_button(self):

        for button_pressed in manette.buttons_pressed:
            action_to_do = self.key_map[button_pressed]

            match action_to_do:
                case "move":
                    self.move(self.sprite_angle)
                case "nothing":
                    "do nothing"

    def step(self):

        self.draw_spaceship(self.sprite_angle)
        self.draw_cannon(self.cannon_sprite_angle)

        self.turning(
            self.direction_cannon, self.cannon_sprite_angle, self.cannon_speed_turn
        )
        self.turning(self.direction, self.sprite_angle, self.sprite_speed_turn)

        if self.is_controlled_by_manette:
            self.handle_button()
            self.direction = manette.movement_axis

            if manette.camera_axis == pygame.Vector2(0, 0):
                self.direction_cannon = self.cannon_sprite_angle
            else:
                self.direction_cannon = manette.camera_axis


player_manette = player_class(
    MIDDLE_SCREEN[0],
    MIDDLE_SCREEN[1],
    10,
    True,
    pygame.image.load("Ships\Medium\\body_02.png").convert_alpha(),
    pygame.image.load("Weapons\Medium\Cannon\\turret_04_mk1.png").convert_alpha(),
    50,
    0.01,
    0.005,
)


def debugging(activate: bool):

    if activate:
        # print(
        #     pygame.transform.rotate(
        #         pygame.image.load("Weapons\Medium\Cannon\\turret_01_mk1.png"), 1
        #     ).get_size()
        # )
        pygame.draw.line(
            screen,
            "red",
            MIDDLE_SCREEN,
            (
                manette.movement_axis.x * 50 + MIDDLE_SCREEN[0],
                manette.movement_axis.y * 50 + MIDDLE_SCREEN[1],
            ),
            5,
        )
        pygame.draw.line(
            screen,
            "green",
            MIDDLE_SCREEN,
            (
                manette.camera_axis.x * 50 + MIDDLE_SCREEN[0],
                manette.camera_axis.y * 50 + MIDDLE_SCREEN[1],
            ),
            5,
        )


while running:

    debugging(1)

    manette.step()
    player_manette.step()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    screen.fill("black")
    clock.tick_busy_loop(fps)
