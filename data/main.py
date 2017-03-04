from . import prepare,tools
from .states import title_screen, gameplay, show_item_screen

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"TITLE": title_screen.TitleScreen(),
                   "GAMEPLAY": gameplay.Gameplay(),
                   "SHOW_ITEM": show_item_screen.ShowItemScreen()}
    controller.setup_states(states, "TITLE")
    controller.main()
