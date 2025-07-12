import pygame
import json

pygame.init()
pygame.display.set_mode((1, 1))
pygame.scrap.init()


def put_to_clipboard(object):
    pygame.scrap.put(pygame.SCRAP_TEXT, str(object).encode("utf-8"))


def color_to_dict(color: pygame.Color):
    return {"r": color.r, "g": color.g, "b": color.b, "a": color.a}


def put_in_palette_txt(list_of_color: list):

    for i, color in enumerate(list_of_color):
        list_of_color[i] = color_to_dict(color)

    with open("palette.txt", "w") as file:
        file.write(json.dumps(list_of_color))


number_of_color = 4
Image = pygame.image.load("palette.png")

all_color_of_palette = []

for i in range(number_of_color):
    all_color_of_palette.append(Image.get_at((i, 0)))

print(all_color_of_palette)


put_in_palette_txt(all_color_of_palette)
