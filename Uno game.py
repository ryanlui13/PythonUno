import os 
import pygame 
import random 

pygame.init()

if not pygame.font:
    print("Font disabled")
if not pygame.mixer:
    print("Sound disabled ")

from collections import Counter 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")   

#load images
def load_image_by_name(name, size=None):
    for ext in (".png", ".jpg", ".jpeg"):
        path = os.path.join(IMAGES_DIR, name + ext)
        if os.path.exists(path):
            surf = pygame.image.load(path).convert_alpha()
            if size:
                surf = pygame.transform.smoothscale(surf, size)
            return surf 
    return None #image is none if image is missng 

#illustrations
def draw_button(screen, rect, text, font, bg_color, text_color):
    pygame.draw.rect(screen, bg_color, rect, border_radius=12)
    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center = rect.center)
    screen.blit(label, label_rect)

    return rect 

def draw_color_buttons(screen, font):
    buttons = {
        "red": pygame.Rect(200, 250, 100, 50),
        "green": pygame.Rect(320, 250, 100, 50),
        "blue": pygame.Rect(440, 250, 100, 50),
        "yellow": pygame.Rect(560, 250, 100, 50),
    }

    draw_button(screen, buttons["red"], "RED", font, (200, 0, 0), (255, 255, 255))
    draw_button(screen, buttons["green"], "GREEN", font, (0, 200, 0), (255, 255, 255))
    draw_button(screen, buttons["blue"], "BLUE", font, (0, 0, 200), (255, 255, 255))
    draw_button(screen, buttons["yellow"], "YELLOW", font, (200, 200, 0), (0, 0, 0))

    return buttons

def check_button_click(event, button_data):
    if event.type != pygame.MOUSEBUTTONDOWN:
        return None 
    mx, my = event.pos
    if isinstance(button_data, dict):
        items = button_data.items()
    else:
        items = button_data 
    
    for result, rect in items:
        if rect.collidepoint(mx, my):
            return result 
    
    return None 

#class for ALL card properties 
class Card():
    def __init__(self, color, value):   #initalize card and their images
        self.color = color
        self.value = value 
        base = f"{self.color}_{self.value}" if self.color != "wild" else f"wild_{self.value}"
        img = load_image_by_name(base, size=(80, 120))
        if img is None:
            print(f"Image not found for {base}")
        self.image = img

    def draw(self, screen, x, y):   #draw cards for the player 
        screen.blit(self.image, (x, y))
    
    def is_match(self, other_card): #check if the player's card can be placed down
        if other_card is None:
            return None 
        return (self.color == other_card.color) or (self.value == other_card.value)
    
    def __str__(self):  #what the user sees
        return f"{self.color} {self.value}" if self.color else self.value
    
    def __repr__(self):
        return f"Card({self.color!r}, {self.value!r})"
        print(player.hand)

class Player(): #integrating player class to make data easier to store / call 
    def __init__(self, name, is_human=True):
        self.name = name
        self.is_human = is_human
        self.hand = []
        self.declared_uno = False   #assume unless otherwise declared later

    def draw_cards(self, deck, num=7):
        for c in range(num):
            if deck:
                self.hand.append(deck.pop())
            else:
                break 
    
    def reset_uno(self):   #reset the game
        self.declared_uno = False 

    def valid_win(self):
        #player wins
        if len(self.hand) == 0:
            return "win"

        if len(self.hand) == 1:
            if not self.declared_uno:
                return "needs_uno"

        return "ok" 
            
class deck():   #deck object
    def __init__(self, color, value, is_wild = False):
        self.color = color 
        self.value = value 
        self.is_value = value 

def card_penalty_value(card):
    if card.value == "+2":
        return 2 
    elif card.value == "+4":
        return 4 
    return 0 

#make sure penalty cards are stacked properly
def is_valid_stack(new_card, top_card, pending_draw):   #pend draw = cards next player needs to draw
    new_penalty = card_penalty_value(new_card)
    if new_penalty == 0:
        return False 
    return new_penalty >= min(4, pending_draw / (pending_draw // new_penalty))  #compare penalty value of new card w/ previous card

def find_stack_card(deck, top_card, pending_draw):
    penalty_cards = [c for c in deck if is_valid_stack(c, top_card, pending_draw)]
    return penalty_cards[0] if penalty_cards else None

def find_normal_Card(deck, top_card):
    matches = [c for c in deck if Card.is_match(c, top_card)]
    return matches[0] if matches else None 

def apply_special_card_effects(card, turn, pending_draw):
    if card.value == "skip":
        return turn + 2, pending_draw 
    elif card.value == "reverse":
        return turn - 1, pending_draw 
    elif card.value == "+2":
        return turn, pending_draw + 2
    elif card.value == "+4":
        return turn, pending_draw + 4
    return turn+1, pending_draw

def draw_until_playable(player, pile, deck, turn, pending_draw, max_draw=50):
    draws = 0
    top_card = pile[-1] 

    while draws < max_draw: 
        if not deck:
            print("deck empty. reshuffling!")
            reshuffle_pile_into_deck(pile, deck)
            if not deck: break 
        
        drawn_card = deck.pop()
        player.hand.append(drawn_card)
        draws += 1

        is_playable = False 
        if pending_draw > 0:
            if is_valid_stack(drawn_card, top_card, pending_draw):
                is_playable = True 
        else:
            if drawn_card.is_match(top_card) or drawn_card.color == "wild":
                is_playable = True 
            
        if is_playable:
            if player.is_human and (drawn_card.color == "wild" or drawn_card.value == "+4"):    #make sure player is human. if so, pause
                msg = f"{player.name} drew and played {drawn_card.value}"
                #insert animation feature to let player know
                return turn, pending_draw, msg
        
            
            player.hand.remove(drawn_card)
            pile.append(drawn_card)

            if not player.is_human and (drawn_card.color == "wild" or drawn_card.value == "+4"):
                drawn_card.color = choose_best_color(player.hand)
            
            return apply_special_card_effects(drawn_card, turn, pending_draw)
    msg = f"{player.name} drew {max_draw} cards. no match was found"
    return turn+1, 0, msg 


def is_move_valid(card, top_card,pending_draw):
    if pending_draw > 0:
        return is_valid_stack(card, top_card, pending_draw)
    return card.is_match(top_card) or card.color == "wild"

def generate_deck():    #random deck for the player 
    colors = ["red", "yellow", "green", "blue"]
    values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "skip", "reverse", "+2"]
    deck = []
    for color in colors:
        deck.append(Card(color, "0"))   #add 2 0s
        for value in values[1:9]:   
            deck.append(Card(color, value))
            deck.append(Card(color, value))

    for _ in range(4):  #wild cards
        deck.append(Card("wild", "+4"))
        deck.append(Card("wild", "wild"))
    
    random.shuffle(deck)  
    return deck 

def check_deck(deck):
    print(f"Total cards: {len(deck)}")

    card_count = Counter((card.color, card.value) for card in deck)

    for card, count in sorted(card_count.items()):
        print(f"{card}: {count}") 

def shuffle_deck(deck): #shuffle deck before new game 
    shuffled_deck = random.shuffle(deck) 
    return shuffled_deck 

def reshuffle_pile_into_deck(pile, deck):
    if len(pile) <= 1:
        return None 
    
    top_card = pile.pop()   #save the top card for next player's reference
    deck.extend(pile)
    pile.clear()

    random.shuffle(deck) #shuffle

def draw_hand(screen, hand, x, y, card_spacing, card_back_surf, show_face=True):
    rects = []
    for i, card in enumerate(hand):
        card_x = x + i * card_spacing 
        card_y = y
        if show_face and card.image:
            screen.blit(card.image, (card_x, card_y))
            rect = pygame.Rect(card_x, card_y, card.image.get_width(), card.image.get_height())
        else: 
            if card_back_surf:
                screen.blit(card_back_surf, (card_x, card_y))
                rect = pygame.Rect(card_x, card_y, card_back_surf.get_width(), card_back_surf.get_height()) #image of opposing player's hand
            else:
                rect = pygame.Rect(card_x, card_y, 80, 120)
            rects.append(rect)
    return rects 

def draw_pile(screen, pile, center):
    if not pile:
        return 
    
    top = pile[-1]  #access top of (pile where players put cards)
    if top.image:
        w, h = top.image.get_size()
        rect = top.image.get_rect(center=center)
        screen.blit(top.image, rect)
    else:
        r = pygame.Rect(center[0]-40, center[1]-60, 80, 120)
        pygame.draw.rect(screen, (200, 200, 200), r)
    
    if pile:    #draw the pile
        top_card = pile[-1]
        top_rect = top_card.image.get_rect(center=(400, 300))
        screen.blit(top_card.image, top_rect)

def animate_card(screen, image_surf, start_pos, end_pos, draw_frame_cb , steps=20, delay_ms=15):
    sx, sy = start_pos 
    ex, ey = end_pos 

    for i in range(1, steps+1):
        t = i/steps 
        x = sx + (ex - sx) * t 
        y = sy + (ey - sy) * t 
        draw_frame_cb(screen) #draw the board + hands 
        if image_surf:
            screen.blit(image_surf, (x,y))
        
        pygame.display.flip()
        pygame.time.delay(delay_ms)

#testing logic to distribute cards 
def distribute_cards_logic(deck, num_cards=7):
    hand = []
    for i in range(num_cards):
        if deck:
            hand.append(deck.pop())
    return hand 

def deal_cards(deck, players, num_cards=7):
    for _ in range(num_cards):
        for player in players:
            if deck:
                player.hand.append(deck.pop())

def deal_cards_with_animation(screen, deck, player, computer, deck_pos, card_back, draw_frame_cb, player_start_pos=None, computer_start_pos=None ,card_spacing = 30):
    for i in range(7):
        card = deck.pop()  #logic based function covers these
        player.hand.append(card)

        end_pos = (100 + i * card_spacing, 500)
        animate_card(screen, card.image, deck_pos, end_pos, draw_frame_cb)

        card = deck.pop()
        computer.hand.append(card)

        end_pos = (100 + i * card_spacing, 50)
        animate_card(screen, card_back, deck_pos, end_pos, draw_frame_cb)
    

def choose_best_color(hand, avoid_color=None):
    counts = {c: 0 for c in ["red", "green", "blue", "yellow"]}

    for card in hand:
        if card.color in counts:
            counts[card.color] += 1 
    
    if avoid_color:
        counts[avoid_color] -= 0.5

    return max(counts, key=counts.get)

def main():
    #game setup
    pygame.init()
    
    screen = pygame.display.set_mode((900, 650))
    font = pygame.font.SysFont('Comic Sans', 30, bold = True)
    
    pygame.display.set_caption("Welcome to UNO with the computer!!!")
    clock = pygame.time.Clock()

    #scenery. Colors for the background
    TABLE_GREEN = (34, 139, 34)

    #images
    card_back_surf = load_image_by_name("card back", size=(80, 120)) or pygame.Surface((80,120))
    shared_deck_surf = load_image_by_name("shared_deck", size=(80, 120)) or card_back_surf
    
    deck = generate_deck()
    player = Player("you", is_human=True)
    computer = Player("Python", is_human=False)

    shared_pos = (400, 260)
    pile = []
    #draw the frame
    def draw_frame(surf):
        surf.fill(TABLE_GREEN)
        surf.blit(shared_deck_surf, (shared_pos[0]-120, shared_pos[1]-20))  #deck, left of center
        draw_pile(surf, pile, center=(shared_pos[0], shared_pos[1]))
        
        draw_hand(surf, player.hand, 50, 500, 30, card_back_surf, show_face=True)
        draw_hand(surf, computer.hand, 50, 50, 30, card_back_surf, show_face=False)

    deal_cards_with_animation(screen, deck, player, computer, (shared_pos[0]-120, shared_pos[1]-20), card_back_surf, draw_frame, player_start_pos=(shared_pos[0], shared_pos[1]), computer_start_pos=(shared_pos[0], shared_pos[1]), card_spacing=30)
    if deck:
        pile.append(deck.pop())
    else:
        reshuffle_pile_into_deck(pile, deck)

    game_message = "Your upp!"
    def draw_message(screen, font, message):
        if not message:
            return 
        text_surf = font.render(message, True, (0, 0, 0))
        pos_x = screen.get_width() // 2 - text_surf.get_width()//2
        pos_y = 20
        
        screen.blit(text_surf, (pos_x, pos_y))
    
    first_rect = pygame.Rect(260, 250, 180, 60)
    comp_rect = pygame.Rect(260, 330, 180, 60)
    uno_rect = pygame.Rect(350, 200, 100, 50)
    catch_rect = pygame.Rect(460, 200, 150, 50)

    ui_buttons = {
        "player_first": first_rect,
        "computer_first": comp_rect,
        "uno": uno_rect,
        "catch": catch_rect,
        "restart": pygame.Rect(350, 400, 200, 60)
    }

    game_state = "choose_first"
    turn = 0
    running = True
    pending_draw = 0
    color_buttons = {}  #empty dict
    wild_color_waiting = None 
    uno_player = None 
    current_player = None

    def draw_ui(screen, game_state, font, buttons):
        if game_state == "choose_first":    
            draw_button(screen, buttons["player_first"], "I will go first", font, (0, 120, 255), (255, 255, 255))
            draw_button(screen, buttons["computer_first"], "computer first!", font, (120, 0, 255), (255, 255, 255))
        elif game_state == "choosing_color":
            return draw_color_buttons(screen, font)
        elif game_state == "wait_for_uno":
            draw_button(screen, buttons["uno"] , "UNO!", font, (255, 0, 0), (255, 255, 255))
            draw_button(screen, buttons["catch"], "CATCH!", font, (0, 0, 0), (255, 255, 255))
        elif game_state == "game_over":
            draw_button(screen, buttons["restart"], "Restart game", font, (50, 50, 50), (255, 255, 255))
            return buttons 
        
        return {}   #no special Ui is active 

    while running:
        draw_frame(screen)#set the game up
        draw_message(screen, font, game_message)
        
        active_buttons = draw_ui(screen, game_state, font, ui_buttons)
        if game_state == "choosing_color":
            color_buttons = active_buttons
        
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "game_over"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "choose_first":
                    mx, my = event.pos 
                    if ui_buttons["player_first"].collidepoint(mx, my):
                        turn = 0
                        game_state = "playing"
                    elif ui_buttons["computer_first"].collidepoint(mx, my):
                        turn = 1
                        game_state = "playing"
                    continue 

                if game_state == "choosing_color":
                    mx, my = event.pos
                    for color, rect in color_buttons.items():
                        if rect.collidepoint(mx, my):
                            wild_color_waiting.color = color 
                            wild_color_waiting = None 
                            choosing_color = False
                            turn, pending_draw = apply_special_card_effects(pile[-1], turn, pending_draw)
                            turn += 1
                    continue
                
                if game_state == "wait_for_uno":
                    mx, my = event.pos
                    if ui_buttons["uno"].collidepoint(mx, my):
                        game_message = f"{uno_player.name} declared UNO!"
                        uno_player.declared_uno = True
                        game_state = "playing" # Return to normal game
                        turn += 1 # Move to the next turn
                        continue
                    elif ui_buttons["catch"].collidepoint(mx, my):
                        game_message = f"CAUGHT! {uno_player.name} draws 2!"
                        for _ in range(2):                          # Add penalty to the person who forgot to say UNO
                            if deck: uno_player.hand.append(deck.pop())
                            
                        game_state = "playing"
                        turn += 1
                        continue
                
                if game_state == "game_over":
                    mx, my = event.pos 
                    if ui_buttons["restart"].collidepoint(mx, my):
                        main()  #restart game loop
                        return 

                if game_state == "playing":
                    if turn%2 == 0: #player's turn
                        current_player = player 
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = event.pos
                            
                            deck_rect = pygame.Rect(300, 200, 100, 150) #deck obej
                            if deck_rect.collidepoint(mx, my):
                                turn, pending_draw, game_message = draw_until_playable(player, pile, deck, turn, pending_draw)
                                continue #leave event check

                            rects = draw_hand(screen, player.hand, 50, 500, 30, card_back_surf, show_face=True)
                            for idx, r in enumerate(rects):
                                if r.collidepoint(mx, my):
                                    chosen = player.hand[idx]
                                    top = pile[-1]
                                    
                                    if is_move_valid(chosen, top, pending_draw):
                                        player.hand.pop(idx)
                                        pile.append(chosen)

                                        if chosen.value in ["wild", "+4"]:
                                            choosing_color = True 
                                            wild_color_waiting = chosen 
                                            break 
                                        
                                        turn, pending_draw = apply_special_card_effects(chosen, turn, pending_draw)
                                    else:
                                        game_message = "You can't play that card right now!"
                            
                            status = player.valid_win()
                            if status == "win":
                                game_message = "you won!"
                                game_state = "game_over" 
                            elif status == "needs_uno":
                                uno_player = player
                                game_state = "wait_for_uno"
                            else:
                                turn += 1

                    if turn %2 != 0 and game_state == "playing":   #computer plays portion
                        current_player = computer
                        pygame.time.delay(400)
                        top = pile[-1]
                        played = False 
                        best_card = None
                        
                        for c in computer.hand:
                            if is_move_valid(c, top, pending_draw):
                                if pending_draw == 0 and c.value not in ["+2", "+4"]:
                                    best_card = c
                                    break 
                                    #computer.hand.remove(c)
                                    #pile.append(c)
                                elif pending_draw > 0:
                                    best_card = c
                                    break 

                                if c.value in ["wild", "+4"]:   #keep it like this
                                    computer.hand.remove(c)
                                    pile.append(c)
                                    c.color = choose_best_color(computer.hand, avoid_color=True)
                                    turn, pending_draw = apply_special_card_effects(c, turn, pending_draw)
                                    played = True 
                                    break 
                        
                        if not best_card:   #find best power card. if all else fails
                            for c in computer.hand:
                                if is_move_valid(c, top, pending_draw):
                                    best_card = c
                                    break 
                                    
                        if best_card:
                            computer.hand.remove(best_card)
                            pile.append(best_card)

                            if best_card.value in ["wild", "+4"]:   #if wild or +4, computer chooses color
                                best_card.color = choose_best_color(computer.hand)
                            
                            turn, pending_draw = apply_special_card_effects(best_card, turn, pending_draw)
                            if best_card.value not in ["reverse", "skip", "+2", "+4", "wild"]:
                                turn += 1
                            played = True 
                        
                        if not played:
                            turn, pending_draw, game_message = draw_until_playable(computer, pile, deck, turn, pending_draw)
            
                status = player.valid_win()
                if status == "win":
                    game_message = f"{player.name} won!"
                    game_state = "game_over"     #break the loop b/c player won

                elif status == "needs_uno":
                    if current_player.is_human:
                        game_state = "wait_for_uno"
                        uno_player = current_player
                    else:
                        current_player.declared_uno = True 
                
                status_comp = computer.valid_win()
                if status_comp == "win":
                    game_message = "Computer won"
                    game_state = "game_over"
    pygame.quit()

if __name__ == "__main__":
    main()


