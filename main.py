import pygame
import json
import random
import socket
import string

pygame.init()
pygame.joystick.init()


screen = pygame.display.set_mode((960, 540), vsync=1, display=0)

MIDDLE_SCREEN = (screen.get_width() / 2, screen.get_height() / 2)


clock = pygame.time.Clock()
running = True
fps = 100


## connection stuff ##


def id_generator(size: int = 5):
    output = []
    for _ in range(size):
        output.append(
            random.choice(
                string.digits + string.ascii_uppercase + string.ascii_lowercase
            )
        )
    return "".join(output)


id = id_generator()

# better to put this at first


class server_class:
    def __init__(self):
        self.address = socket.gethostbyname(
            socket.gethostname()
        )  # it's host so it's own ip
        self.port = 5000


server = server_class()


class client_class:
    def connect(
        self, port: int, addr: str = socket.gethostbyname(socket.gethostname())
    ):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((addr, port))
        return s

    def __init__(self):
        self.port = 5000 + random.randint(1, 1000)
        self.address = socket.gethostbyname(socket.gethostname())

        print("port=", self.port, "addr=", self.address)
        print("triying connect to", server.port, ",", server.address)

        self.socket = self.connect(server.port, server.address)
        print("connected to", server.port, ",", server.address)
        self.send_to_server(str(player_keyboard))

    def get_0_before_int(self, number: int | str, length_expected: int) -> str:
        """get 0 before the int so it correspond to a certain length (eg: input 1,4 it will output 0001)"""
        if isinstance(number, int):
            number = str(number)

        number_length = len(number)
        if number_length > length_expected:
            raise ValueError(
                "Number length is greater to expected length, increment expected length or lower number"
            )
        for _ in range(length_expected - number_length):
            number = "0" + number

        return number

    def send_to_server(self, info: str, intro_length: int = 4):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the server and in the client"""

        output_to_send = self.get_0_before_int(info.__len__(), intro_length) + info

        self.socket.send(output_to_send.encode("utf-8"))

    def receive_from_server(self, intro_length: int = 4):
        """the intro length is the number of number that is sent at start of message to give the length of the message \n
        it should be the same in the server and in the client"""

        length_of_message = self.socket.recv(intro_length)
        length_of_message = length_of_message.decode("utf-8")

        if length_of_message == "":  # 'cause it's disconnected if it received that
            return None

        length_of_message = int(length_of_message)

        output = self.socket.recv(length_of_message)

        output = output.decode("utf-8")

        return output

    def step(self):

        client.send_to_server(
            str(player_keyboard)
        )  # must be before receive 'cause server is receive then send
        message = self.receive_from_server()

        if message == "":
            self.disconnect()

            global running
            running = False

        else:
            print(message, "received")

    def disconnect(self):
        print("disconnected :<")
        self.socket.shutdown(1)
        self.socket.close()
        self.is_client_connected_to_server = False


## camera and all screen stuff ##
all_cameras = []


class camera_class:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.screen = pygame.Surface((rect.width, rect.height))
        all_cameras.append(self)

    def reset_screen(self):  # must be called
        self.screen.fill("black")

    def show_on_camera(
        self, image: pygame.Surface, destination: pygame.Rect | tuple[int, int]
    ):
        if isinstance(destination, tuple):
            destination = image.get_rect(x=destination[0], y=destination[1])

        relative_destination = pygame.Rect(
            destination.x - self.rect.x,
            destination.y - self.rect.y,
            destination.width,
            destination.height,
        )

        if self.rect.colliderect(
            destination
        ):  # check if it's in the screen (optimization)
            self.screen.blit(image, relative_destination)


camera_keyboard = camera_class(
    pygame.Rect(0, 0, screen.get_width(), screen.get_height())
)


def show(image: pygame.Surface, destination: pygame.Rect | tuple[int, int]):
    """
    make an image appering to camera
    """

    if isinstance(destination, tuple):
        destination = image.get_rect(x=destination[0], y=destination[1])

    for camera in all_cameras:
        camera: camera_class
        camera.show_on_camera(image, destination)


## keyboard and mouse ##
class keyboard_class:
    def __init__(self):
        self.pressed_keys = []
        self.mouse_position = pygame.Vector2(pygame.mouse.get_pos())

        self.click_map = {
            0: "left click",
            1: "right click",
            2: "middle click",
            3: "near click",  # the button on the side that's near the hand (fourth button)
            4: "far click",  # the button on the side that's far to the hand (fifth button)
        }

    def key_press(self, key):
        self.pressed_keys.append(pygame.key.name(key))

    def key_release(self, key):
        self.pressed_keys.remove(pygame.key.name(key))

    def step(self):

        self.mouse_position = pygame.Vector2(pygame.mouse.get_pos())

        clicks_pressed = pygame.mouse.get_pressed(5)

        for click_checked in range(5):
            if clicks_pressed[click_checked]:
                if self.click_map[click_checked] not in self.pressed_keys:
                    self.pressed_keys.append(self.click_map[click_checked])
            elif self.click_map[click_checked] in self.pressed_keys:
                self.pressed_keys.remove(self.click_map[click_checked])


keyboard = keyboard_class()


## bullet ##

all_bullets = []  # list of all instance of bullet (idk where to put it..)


class bullet_class(pygame.sprite.Sprite):
    def __init__(
        self,
        x: float,
        y: float,
        image: pygame.Surface,
        speed: float,
        direction: pygame.Vector2,
        origine,  # can't put :player_class 'cause it's defined after bullet
    ):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y

        self.image = image

        self.speed = speed
        self.mask = pygame.Mask((image.get_rect().width, image.get_rect().height), True)
        self.rect = self.image.get_rect()

        self.direction = direction

        self.exist = True
        all_bullets.append(self)

    def step(self):
        if self.exist:

            self.move()

            self.draw_self(self.direction)

            # if pygame.sprite.collide_mask(
            #     self, self.object_to_check_collision
            # ):  # collision with other player

            #     self.destroy()

    def draw_self(self, image_angle: pygame.Vector2):

        rotated_image = pygame.transform.rotate(
            self.image, -image_angle.as_polar()[1] - 90
        )

        rect_image_rotated = rotated_image.get_rect(
            center=(
                self.x,
                self.y,
            )
        )

        # updating each time the sprite moves or rotate
        self.mask = pygame.mask.from_surface(rotated_image)
        self.rect = rect_image_rotated

        show(rotated_image, rect_image_rotated)

    def move(self):
        self.x += self.direction.x * self.speed
        self.y += self.direction.y * self.speed

    def destroy(self):
        self.exist = False
        all_bullets.remove(self)


## player ##


class player_class(pygame.sprite.Sprite):

    def __init__(
        self,
        x: int,
        y: int,
        direction: int,
        camera: camera_class,
        image: pygame.Surface,
        cannon_image: pygame.Surface,
        bullet_image: pygame.Surface,
        speed_per_sec: int,
        cannon_speed_turn: float,
        image_speed_turn: float,
        bullet_speed: float,
        bullet_reload_time: float,
    ):
        pygame.sprite.Sprite.__init__(self)

        self.x = x
        self.y = y

        self.camera = camera

        self.camera_rect = self.camera.rect
        self.MIDDLE_SCREEN = (self.camera_rect.width / 2, self.camera_rect.height / 2)

        self.camera_rect.x = x - self.MIDDLE_SCREEN[0]
        self.camera_rect.y = y - self.MIDDLE_SCREEN[1]

        self.image = image  # the spaceship
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = image.get_rect()

        self.cannon_image = cannon_image
        self.bullet_image = bullet_image

        self.direction = pygame.Vector2.from_polar((1, direction))
        self.direction: pygame.Vector2
        self.image_angle = self.direction.copy()
        # the direction is where it wants to be watching, the objective
        # the image angle is where it is watching
        self.direction_cannon = self.direction.copy()
        self.relative_direction_cannon = self.direction.copy()
        self.cannon_image_angle = self.direction.copy()

        self.max_speed = speed_per_sec / fps

        self.cannon_speed_turn = cannon_speed_turn
        self.image_speed_turn = image_speed_turn
        self.bullet_speed = bullet_speed

        self.bullet_reload_time = bullet_reload_time
        self.tick_since_last_bullet = 0

        self.key_map = {
            "d": "turn right",
            "q": "turn left",
            "z": "move",
            "left click": "shoot",
        }

    def __str__(self):
        return json.dumps(
            {
                "type": "player info",
                "id": id,
                "x": round(self.x),
                "y": round(self.y),
                "image_angle": round(self.image_angle.as_polar()[1], 1),
                "cannon_image_angle": round(self.cannon_image_angle.as_polar()[1], 1),
            }
        )

    def __repr__(self):
        return self.__str__()

    def draw_spaceship(self, image_angle: pygame.Vector2):
        rotated_image = pygame.transform.rotate(
            self.image, -image_angle.as_polar()[1] - 90
        )

        rect_image_rotated = rotated_image.get_rect(center=(self.x, self.y))

        # updating each time the sprite moves or rotate
        self.mask = pygame.mask.from_surface(rotated_image)
        self.rect = rect_image_rotated

        show(rotated_image, rect_image_rotated)

    def draw_cannon(self, image_angle: pygame.Vector2):

        rotated_cannon_image = pygame.transform.rotate(
            self.cannon_image, -image_angle.as_polar()[1] - 90
        )

        rect_cannon_image_rotated = rotated_cannon_image.get_rect(
            center=(self.x, self.y)
        )

        show(rotated_cannon_image, rect_cannon_image_rotated)

    def camera_follow_self(self, camera: camera_class):
        camera.rect.center = (self.x, self.y)

    def get_coordinates_relative_to_screen(self, x, y):
        return pygame.Vector2(x - self.camera_rect.x, y - self.camera_rect.y)

    def turning(
        self,
        vector_to_turn_too: pygame.Vector2,
        vector_turning: pygame.Vector2,
        speed: float,
    ):

        speed_per_second = speed / fps  # in degrees

        if (
            vector_turning != vector_to_turn_too
            and vector_to_turn_too != pygame.Vector2(0, 0)
        ):

            angle_between_vector = pygame.math.Vector2.angle_to(
                vector_turning, vector_to_turn_too
            )

            if speed_per_second > abs(
                angle_between_vector
            ):  # anti vibration(must be before everything otherwise it don't work)
                vector_turning = vector_to_turn_too

            if angle_between_vector < 0:

                if abs(angle_between_vector) < 180:
                    output_vector = pygame.math.Vector2.rotate(
                        vector_turning, -speed_per_second
                    )

                else:
                    output_vector = pygame.math.Vector2.rotate(
                        vector_turning, speed_per_second
                    )

            else:

                if abs(angle_between_vector) < 180:
                    output_vector = pygame.math.Vector2.rotate(
                        vector_turning, speed_per_second
                    )
                else:
                    output_vector = pygame.math.Vector2.rotate(
                        vector_turning, -speed_per_second
                    )
            return output_vector

        else:
            return vector_turning

    def turn_right(self, vector_turning: pygame.Vector2, speed: float):

        vector_output = vector_turning.copy()
        return vector_output.rotate(speed / fps)

    def turn_left(self, vector_turning: pygame.Vector2, speed: float):

        vector_output = vector_turning.copy()
        return vector_output.rotate(-speed / fps)

    def move(self, speed: pygame.Vector2):
        self.x += speed.x
        self.y += speed.y

    def get_direction_relative_to_another(
        self, reference_direction: pygame.Vector2, moving_direction: pygame.Vector2
    ):
        return moving_direction.rotate(reference_direction.as_polar()[1])

    def handle_key_press(self):

        for key_pressed in keyboard.pressed_keys:
            if key_pressed in self.key_map:
                action_to_do = self.key_map[key_pressed]

                match action_to_do:
                    case "move":
                        self.move(self.image_angle)
                    case "shoot":
                        self.shoot()
                    case "nothing":
                        "do nothing"
                    case "turn right":
                        self.image_angle = self.turn_right(
                            self.image_angle, self.image_speed_turn
                        )
                    case "turn left":
                        self.image_angle = self.turn_left(
                            self.image_angle, self.image_speed_turn
                        )

    def get_mouse_position_relative_to_player(self):
        return pygame.Vector2(
            (keyboard.mouse_position.x - MIDDLE_SCREEN[0]) - self.MIDDLE_SCREEN[0],
            keyboard.mouse_position.y - self.MIDDLE_SCREEN[1],
        )

    def update_rect_to_position(self):
        rect_output = self.rect.copy()
        rect_output.x = self.x
        rect_output.y = self.y
        return rect_output

    def shoot(self):
        if self.tick_since_last_bullet == self.bullet_reload_time:
            self.tick_since_last_bullet = 0
            return bullet_class(
                self.x,
                self.y,
                self.bullet_image,
                self.bullet_speed,
                self.cannon_image_angle,
                self,
            )

    def step(self):

        self.draw_spaceship(self.image_angle)
        self.draw_cannon(self.cannon_image_angle)

        self.camera_follow_self(self.camera)

        self.cannon_image_angle = self.turning(
            self.relative_direction_cannon,
            self.cannon_image_angle,
            self.cannon_speed_turn,
        )

        if self.tick_since_last_bullet < self.bullet_reload_time:
            self.tick_since_last_bullet += 1

        self.handle_key_press()
        self.cannon_image_angle = self.turning(
            self.direction_cannon, self.cannon_image_angle, self.cannon_speed_turn
        )
        mouse_position_relative = self.get_mouse_position_relative_to_player()

        if keyboard.mouse_position == pygame.Vector2(0, 0):
            self.direction_cannon = self.cannon_image_angle
        else:
            self.direction_cannon = mouse_position_relative.normalize()
        pygame.draw.line(screen, "red", (0, 0), mouse_position_relative, 10)


player_keyboard = player_class(
    MIDDLE_SCREEN[0],
    MIDDLE_SCREEN[1],
    10,
    camera_keyboard,
    pygame.image.load("Ships\Medium\\body_03.png").convert_alpha(),
    pygame.image.load("Weapons\Medium\Cannon\\turret_04_mk1.png").convert_alpha(),
    pygame.image.load("Weapons\Small\Cannon\\turret_01_bullet_01.png").convert_alpha(),
    50,
    200,  # degrees per second
    100,  # degrees per second
    10,
    10,
)


client = client_class()

while running:

    for bullet in all_bullets:
        bullet: bullet_class
        bullet.step()

    keyboard.step()

    client.step()

    player_keyboard.step()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            keyboard.key_press(event.key)

        elif event.type == pygame.KEYUP:
            keyboard.key_release(event.key)

    screen.blit(camera_keyboard.screen, (0, 0))

    pygame.display.flip()
    screen.fill("black")

    camera_keyboard.reset_screen()

    clock.tick_busy_loop(fps)

"""
todo:
    explosion on impact of bullet

"""
