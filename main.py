import pygetwindow
from pyscreeze import ImageNotFoundException
import pyautogui as pag
from PIL import Image
from pynput import keyboard
import time

path = "./screenshots/window_screenshot.png"
title = "Legends Of Idleon"

def get_window():
    window = pygetwindow.getWindowsWithTitle(title)[0]

    window_dict = {
        "window": window,
        "left": window.left, 
        "right": window.right,
        "top": window.top,
        "bottom": window.bottom,
        "size": window.size
    }

    return window_dict

def get_screenshot():
    window_dict = get_window()
    pag.screenshot(path)
    image = Image.open(path)
    image = image.crop((window_dict["left"], window_dict["top"], window_dict["right"], window_dict["bottom"]))
    image.save(path)

def filter_and_sort_cards(cards_list):
    filtered_cards = []
    for card in cards_list:
        is_duplicate = False
        for existing_card in filtered_cards:
            # If centers are within 10 pixels, it"s the same card
            if (abs(card.left - existing_card.left) < 25 and 
                abs(card.top - existing_card.top) < 25):
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_cards.append(card)

    filtered_cards.sort(key=lambda c: (c.top // 10, c.left))
    
    return filtered_cards

def get_cards():
    try:
        cards_list = list(pag.locateAll("screenshots/card_border.png", path, confidence=0.90))
        game_window = Image.open(path)

        filtered_cards = filter_and_sort_cards(cards_list)

        for i, card in enumerate(filtered_cards):
            card_image = game_window.crop((
                card.left - 5, 
                card.top - 3, 
                card.left + card.width + 140, 
                card.top + card.height + 5,
            ))
            card_image.save(f"screenshots/cards/card{i+1}.png")
        
        return filtered_cards
    except ImageNotFoundException:
        print("No cards found.")

def is_position_click(center, clicked_positions):
    for clicked in clicked_positions:
        if abs(center.x - clicked.x) < 10 and abs(center.y - clicked.y) < 10:
            return True
    return False

def get_second_card(card_number, clicked_positions):
    card_matches = list(pag.locateAll(f"screenshots/cards/card{card_number}.png", path, confidence=0.95))

    filtered_card_matches = filter_and_sort_cards(card_matches)

    unclicked_matches = [
        match for match in filtered_card_matches
        if not is_position_click(pag.center(match), clicked_positions)
    ]

    if len(unclicked_matches) == 2:
        return pag.center(unclicked_matches[0]), pag.center(unclicked_matches[1])
    
    return None, None
    
def on_press(key):
    try:
        if key.char == "f":
            print("Clicked f")

            while True:
                get_screenshot()

                cards = get_cards()

                if not cards:
                    print("Error: No card in cards!")
                    return

                time.sleep(1)

                clicked_positions = []
                for i in range(len(cards)):
                    original_card, matching_card = get_second_card(f"{i+1}", clicked_positions)
                    if original_card and matching_card:
                        pag.moveTo(original_card, duration=0.2)
                        pag.click()
                        pag.moveTo(matching_card, duration=0.2)
                        pag.click()
                        clicked_positions.append(original_card)
                        clicked_positions.append(matching_card)
                    else:
                        print(f"{i+1} is already clicked")

                time.sleep(4)            
    except AttributeError:
        pass

def main():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()     

if __name__ == "__main__":
    main()