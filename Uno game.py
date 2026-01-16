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
        if value in ["wild", "+4"]:
            self.color = "wild"
        
        base = f"{self.color}_{self.value}" if self.color != "wild" else f"wild_{self.value}"
        img = load_image_by_name(base, size=(80, 120))
        self.image = img

    def draw(self, screen, x, y):   #draw cards for the player 
        screen.blit(self.image, (x, y))
    
    def is_match(self, other_card): #check if the player's card can be placed down
        if other_card is None:
            return True 
        if self.color == "wild":
            return True 
        
        return (self.color == other_card.color) or (self.value == other_card.value) #normal valid card to play
    
    def __str__(self):  #what the user sees
        return f"{self.color} {self.value}" if self.color else self.value
    
    def __repr__(self):
        return f"Card({self.color!r}, {self.value!r})"

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
    new_val = new_card.value
    top_val = top_card.value

    if new_val == top_val:
        return True
    elif new_val == "+2" and top_val == "+4":
        return True 
    elif new_val == "+4" and top_val == "+4":
        return True 
    else:
        return False

def find_stack_card(deck, top_card, pending_draw):
    penalty_cards = [c for c in deck if is_valid_stack(c, top_card, pending_draw)]
    return penalty_cards[0] if penalty_cards else None

def find_normal_Card(deck, top_card):
    matches = [c for c in deck if Card.is_match(c, top_card)]
    return matches[0] if matches else None 

def apply_special_card_effects(card, pending_draw):
    if card.value == "skip":
        return pending_draw, f"Skip! Player was skipped" 
    elif card.value == "reverse":
        return pending_draw, "Reverse .. reverse! It's your turn now!"
    elif card.value == "+2":
        return pending_draw + 2, "Draw 2!"
    elif card.value == "+4":
        return pending_draw + 4, "Wild Draw 4!"
    return pending_draw, ""

def draw_until_playable(player, pile, deck, turn, pending_draw, screen, draw_frame, max_draw=50):
    draws = 0
    top_card = pile[-1] 
    is_playable = False 

    required_draws = pending_draw if pending_draw > 0 else 1

    while draws < max_draw: 
        pygame.event.pump() #prevent freezing
        if not deck:
            reshuffle_pile_into_deck(pile, deck)
            if not deck: break 
        
        drawn_card = deck.pop()
        player.hand.append(drawn_card)
        draws += 1

        draw_frame(screen)
        pygame.display.flip()
        pygame.time.delay(400)

        if pending_draw > 0:
            if draws < pending_draw:
                continue 
            else:
                return turn, 0, f"{player.name} drew {draws} cards"
            
        else:
            if drawn_card.is_match(top_card) or drawn_card.color == "wild":
                return turn, 0, f"{player.name} drew a playable card!"
        
    msg = f"{player.name} drew {max_draw} cards. no match was found"
    return turn + 1, 0, msg 


def is_move_valid(chosen_card, top_card,pending_draw):
    if pending_draw > 0:
        if top_card.value == "+2":
            return chosen_card.value in ["+2", "+4"]
        if top_card.value == "+4":
            return chosen_card.value == "+4"
        return False #in case of some penalty
    if chosen_card.color == "wild":
        return True 
    
    return (chosen_card.color == top_card.color or chosen_card.value == top_card.value)

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
    card_count = Counter((card.color, card.value) for card in deck)
 

def shuffle_deck(deck): #shuffle deck before new game 
    shuffled_deck = random.shuffle(deck) 
    return shuffled_deck 

def reshuffle_pile_into_deck(pile, deck):
    if len(pile) <= 1:
        return 
    
    top_card = pile[-1]   #save the top card for next player's reference
    cards_to_shuffle = pile[:-1]
    
    deck.extend(cards_to_shuffle)
    random.shuffle(deck)

    pile.clear()
    pile.append(top_card)

def draw_hand(screen, hand, x, y, card_spacing, card_back_surf, show_face=True):
    rects = []
    for i, card in enumerate(hand):
        card_x = x + i * card_spacing 
        card_y = y
        if show_face and card.image:
            screen.blit(card.image, (card_x, card_y))
            rect = pygame.Rect(card_x, card_y, 80, 120)
        else: 
            if card_back_surf:
                screen.blit(card_back_surf, (card_x, card_y))
            else:
                pygame.draw.rect(screen, (200, 0, 0), (card_x, card_y, 80, 120))
            
            rect = pygame.Rect(card_x, card_y, 80, 120)
        
        rects.append(rect)
    return rects 

def draw_pile(screen, pile, center):
    if not pile:
        return 
    
    top_card = pile[-1]  #access top of (pile where players put cards)
    if top_card.image:
        rect = top_card.image.get_rect(center=center)
        screen.blit(top_card.image, rect)
    else:
        r = pygame.Rect(center[0]-40, center[1]-60, 80, 120)
        pygame.draw.rect(screen, (200, 200, 200), r)
    
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
    
    screen = pygame.display.set_mode((1280, 720))
    font = pygame.font.SysFont('Comic Sans', 30, bold = True)
    
    pygame.display.set_caption("Welcome to UNO with the computer!!!")
    clock = pygame.time.Clock()

    #scenery. Colors for the background
    WHITE = (255, 255, 255)
    TABLE_BLUE = (10, 25, 47)

    #images
    card_back_surf = load_image_by_name("card_back", size=(80, 120))
    shared_deck_surf = load_image_by_name("shared_deck", size=(80, 120)) or card_back_surf
    
    #deck positions and set up
    shared_pos = (screen.get_width() // 2, screen.get_height() // 2)
    deck_x = shared_pos[0] - 220
    deck_y = shared_pos[1] - 20
    DECK_POS = (deck_x, deck_y)
    deck_rect = pygame.Rect(DECK_POS[0], DECK_POS[1], 80, 120)
    deck = generate_deck()

    #set player and computer up
    player = Player("you", is_human=True)
    computer = Player("Python", is_human=False)

    pile = []
    #draw the frame
    def draw_frame(surf):
        surf.fill(TABLE_BLUE)
        surf.blit(shared_deck_surf, (shared_pos[0]-200, shared_pos[1]-20))  #deck, left of center
        draw_pile(surf, pile, center=(shared_pos[0], shared_pos[1]))
        
        draw_hand(surf, player.hand, 50, 520, 30, card_back_surf, show_face=True)
        draw_hand(surf, computer.hand, 50, 50, 50, card_back_surf, show_face=False)

    deal_cards_with_animation(screen, deck, player, computer, (shared_pos[0]-200, shared_pos[1]-20), card_back_surf, draw_frame, player_start_pos=(shared_pos[0], shared_pos[1]), computer_start_pos=(shared_pos[0], shared_pos[1]), card_spacing=30)
    if deck:
        pile.append(deck.pop())
    else:
        reshuffle_pile_into_deck(pile, deck)

    valid_start = False
    while not valid_start:
        first_card = deck.pop()
        if first_card.color != "wild" and first_card.value not in ["+2", "+4", "skip", "reverse"]:
            pile.append(first_card)
            valid_start = True 
        else:
            deck.insert(0, first_card)  #put the card back into deck
            random.shuffle(deck)
        
    game_message = "Your upp!"
    def draw_message(screen, font, message):
        if not message:
            return 
        text_surf = font.render(message, True, (255, 255, 255))
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
        "restart": pygame.Rect(350, 400, 200, 60),
        "end_turn": pygame.Rect(700, 400, 150, 50)
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
        elif game_state == "playing" and turn %2 == 0:
            if card_played_this_turn and pending_draw == 0:
                draw_button(screen, buttons["end_turn"], "END TURN!", font, (50, 200, 50), (255, 255, 255))
        
        return {}   #no special Ui is active 

    turn = 0
    last_turn = -1
    card_played_this_turn = False 

    while running:
        current_player = player 
        if game_state == "playing":
            if turn % 2 == 0: # player's turn
                if last_turn != turn:
                    card_played_this_turn = False 
                    last_turn = turn 
                    game_message = "Your turn!"                        
                else:
                    if last_turn != turn:
                        last_turn = turn 
                        game_message = "computer is thinking...Playing..."
        
        #refresh the drawing after every frame
        draw_frame(screen)
        player_rects = draw_hand(screen, player.hand, 50, 520, 30, card_back_surf, show_face=True)
        draw_message(screen, font, game_message)
        active_buttons = draw_ui(screen, game_state, font, ui_buttons)
        if game_state == "choosing_color":
            color_buttons = active_buttons 
        
        pygame.display.flip()
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "game_over"
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:    #have game states first
                mx, my = event.pos
                if game_state == "choose_first":
                    if ui_buttons["player_first"].collidepoint(mx, my):
                        game_state = "playing"
                        turn = 0
                        current_player = player 
                        continue 
                    elif ui_buttons["computer_first"].collidepoint(mx, my):
                        game_state = "playing"
                        turn = 1
                        current_player = computer
                        continue  
                
                #end game
                elif game_state == "game_over": 
                    mx, my = event.pos 
                    if ui_buttons["restart"].collidepoint(mx, my):
                        running = False  #restart game loop
                        return 

                #choose color
                elif game_state == "choosing_color":
                    mx, my = event.pos
                    for color, rect in color_buttons.items():
                        if rect.collidepoint(mx, my):
                            top_card = pile[-1]
                            top_card.color = color 
                            base = f"{color}_{top_card.value}"

                            new_img = load_image_by_name(base, size=(80, 120))
                            if new_img:
                                top_card.image = new_img 

                            pending_draw, game_message = apply_special_card_effects(pile[-1], pending_draw)
                            wild_color_waiting = None 
                            turn += 1
                            game_state = "playing"
                            break 
                
                #uno game
                elif game_state == "wait_for_uno":
                    mx, my = event.pos
                    if ui_buttons["uno"].collidepoint(mx, my):
                        game_message = f"{uno_player.name} declared UNO!"
                        uno_player.declared_uno = True
                        game_state = "playing" # Return to normal game
                        turn += 1 # Move to the next turn
                    
                    elif ui_buttons["catch"].collidepoint(mx, my):
                        game_message = f"CAUGHT! {uno_player.name} draws 2!"
                        for _ in range(2):                          # Add penalty to the person who forgot to say UNO
                            if deck: 
                                uno_player.hand.append(deck.pop())
                                draw_frame(screen)
                                pygame.display.flip()
                                pygame.time.delay(250)
                            
                        game_state = "playing"
                        turn += 1
                    
                    continue

                elif game_state == "playing" and turn % 2 == 0:
                    #end turn button
                    if ui_buttons["end_turn"].collidepoint(mx, my):
                        if card_played_this_turn and pending_draw == 0:
                            turn += 1
                            card_played_this_turn = False 
                            game_message = "Computer turn"
                            continue 

                    if deck_rect.collidepoint(mx, my) and not card_played_this_turn:
                        turn, pending_draw, game_message = draw_until_playable(player, pile, deck, turn, pending_draw, screen, draw_frame)    #draw the card
                        card_played_this_turn = True 
                        turn += 1
                        game_message = "You drew cards. the computer goes now..."
                        continue 
                            
                    for idx in range(len(player_rects) - 1, -1, -1):
                        r = player_rects[idx]   #holds the card object 
                        if r.collidepoint(mx, my):
                            chosen = player.hand[idx]
                            top = pile[-1]
                                        
                            if is_move_valid(chosen, top, pending_draw):    #allows penalty stacking
                                if card_played_this_turn and chosen.value != "wild" and chosen.value != top.value:
                                    game_message = "values must match"
                                    break 

                                player.hand.pop(idx)    #get the index of the card 
                                pile.append(chosen) #add card obj to pile
                                card_played_this_turn = True 
                                game_message = "Played! stack or end!"

                                if chosen.value in ["skip", "reverse"]:
                                    pending_draw, game_message = apply_special_card_effects(chosen, pending_draw)
                                    turn += 2 #2 player game so skip and reverse are the same 
                                
                                if chosen.value in ["+2", "+4"]:    #+2 penalty
                                    pending_draw, game_message = apply_special_card_effects(chosen, pending_draw) 
                                    game_message = f"Stack a {chosen.value} or end turn!!"
                                    turn += 1

                                if chosen.value in ["wild", "+4"]:  #+4 penalty
                                    game_state = "choosing_color" # Use state instead of variable
                                    wild_color_waiting = chosen 
                        
                                break  #stop loop for any valid card play
                    
        if not pile:
            if deck:
                pile.append(deck.pop())
            else:
                game_message = "Deck and pile are both empty. Error!"
        
        top = pile[-1]

        if game_state == "playing" and turn % 2 != 0:   #computer plays portion
            current_player = computer
            pygame.time.delay(2000)
            pygame.event.pump() #responsive window
            top = pile[-1]
            
            playable_cards = [c for c in computer.hand if is_move_valid(c, top, pending_draw)]

            if playable_cards:  #choose the playable card
                #separate normal cards from +2 and +4
                normal_cards = [c for c in playable_cards if c.value not in ["+2", "+4"]]
                power_cards = [p for p in playable_cards if p.value in ["+2", "+4"]]

                if pending_draw > 0:    #if penalty on pile, computer tries to play a power card
                    valid_power_cards = [p for p in power_cards if p.value == top.value or p.value == "+4"]
                    chosen_card = valid_power_cards[0] if valid_power_cards else None 
                else:
                    chosen_card = normal_cards[0] if normal_cards else power_cards[0]
                
                if chosen_card:
                    if chosen_card.value in ["wild", "+4"]:
                        new_color = choose_best_color(computer.hand)
                        chosen_card.color = new_color
                        base = f"{new_color}_{chosen_card.value}"

                        chosen_card.image = load_image_by_name(base, size=(80,120))
                        game_message = f"Computer chose {new_color.upper()}!"
                        turn += 1
                        card_played_this_turn = False 
                        continue

                    if chosen_card.value in ["skip", "reverse"]:
                        pending_draw, game_message = apply_special_card_effects(chosen_card, pending_draw) 
                        turn += 2
                    
                    pending_draw, game_message = apply_special_card_effects(chosen_card, pending_draw)
                    computer.hand.remove(chosen_card)
                    pile.append(chosen_card)
                    game_message = f"Computer played {chosen_card.value}!"
                    draw_frame(screen)
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    
                    turn += 1
                    continue    #leave computer's turn
            
            else:
                _, pending_draw, game_message = draw_until_playable(computer, pile, deck, turn, pending_draw, screen, draw_frame)
                game_message = "Computer drew cards. "
                turn += 1
            
            draw_frame(screen)
            pygame.display.flip()
            card_played_this_turn = False 
            
        if game_state == "playing" and current_player is not None:
            status = current_player.valid_win()
            if status == "win":
                game_message = f"{current_player.name} won!"
                game_state = "game_over"     #break the loop b/c player won

            elif status == "needs_uno":
                if current_player.is_human:
                    game_state = "wait_for_uno"
                    uno_player = current_player
                else:
                    current_player.declared_uno = True 
                    game_message = f"{current_player.name} said UNO!"
                    turn += 1

    pygame.quit()

if __name__ == "__main__":
    main()


