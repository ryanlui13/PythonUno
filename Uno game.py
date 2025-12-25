import os 
import pygame 
import random 

pygame.init()

if not pygame.font:
    print("Font disabled")
if not pygame.mixer:
    print("Sound disabled ")

from collections import Counter 

BASE_DIR = os.pat.dirname(os.path.abspath(__file__))
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


#class for ALL card properties 
class Card():
    def __init__(self, color, value):   #initalize card and their images
        self.color = color
        self.value = value 
        base = f"{self.color}_{self.value}" if self.color != "wild" else f"wild_{self.value}"
        img = load_image_by_name(base, size=(80, 120))
        if img is None:
            print(f"Image not found for {base}")
        self.image = self.load_image()

    def draw(self, screen, x, y):   #draw cards for the player 
        screen.blit(self.image, (x, y))
    
    def is_match(self, other_card): #check if the player's card can be placed down
        if other is None:
            return None 
        return (self.color == other.color) or (self.value == other.value)
    
    def __str__(self):  #what the user sees
        return f"{self.color} {self.value}" if self.color else self.value
    
    def __repr__(self):
        return f"Card({self.color!r}, {self.value!r})"
        print(player.hand)

class player(): #integrating player class to make data easier to store / call 
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
        if len(self.hand) > 1:
            self.declared_uno = False 
            return False, False #(won, has uno)
        
        #player wins
        if len(self.hand) == 0:
            print(f"{self.name} won the game.")
            return True, False 
        
        if len(self.hand) == 1:
            if self.is_human:
                response = input(f"{self.name}, declare 'uno' to avoid penalty").strip().lower()
                if response == "uno":
                    self.declared_uno = True 
                    return False, True 
                else:
                    print("Draw 2 cards. ")
                    self.draw_cards(deck, 2)
                    return False, False 
            
            else:   #computer is called
                print(f"{self.name} declared uno!")
                self.declared_uno = True    #automatic
                return False, True

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
        return pending_draw + 2
    elif card.value == "+4":
        return pending_draw + 4
    return pending_draw

def draw_until_playable(player, pile, deck, turn, pending_draw, max_draw=50):
    drawn_card = deck.pop()
    draws = 0
    top_card = pile[-1] 

    while draws < max_draws: 
        for card in list(player.hand):
            if (pending_draw > 0 and is_valid_stack(card, top_card, pending_draw) or (pending_draw==0 and Card.is_match(card, top_card))):
                player.hand.remove(card)
                pile.append(card)
                return apply_special_card_effects(card, turn, pending_draw)
        draws += 1
    
    if draws >= max_draw:
        print("Max drawings is reached.") 

    if not deck:
        print("deck empty. reshuffling!")
        reshuffle_pile_into_deck(pile, deck)
    
    drawn_card = deck.pop()
    player.hand.append(drawn_card)
    draws += 1
    print(f"{player.name} drew a card: {drawn_card}")
    
    if (pending_draw > 0 and is_valid_stack(drawn_card, top_card, pending_draw) or (pending_draw == 0 and Card.is_match(drawn_card, top_card))):
        player.hand.remove(drawn_card)  #choosen card
        pile.append(drawn_card)
        return apply_special_card_effects(drawn_card, turn, pending_draw=0)

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

    reshuffled_cards = random.shuffle(deck) #shuffle
    deck.extend(reshuffled_cards)    #shuffled cards are the new deck

def draw_hand(screen, hand, x, y, card_spacing, card_back_surf, show_face=True):
    rects = []
    for i, card in enumerate(hand):
        card_x = x + i * card_spacing 
        card_y = y
        if show_face and card.image:
            screenblit(card.image, (card_x, card_y))
            rect = pygame.Rect(card_x, card_y, card.image.get_width(), card.image.get_height())
        else: 
            if card_back_surf:
                screen.blit(card_back,_surf, (card_x, card_y))
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
        pyganme.draw.rect(screen, (200, 200, 200), r)
    
    if pile:    #draw the pile
        top_card = pile[-1]
        top_rect = top_card.image.rect(center=(400, 300))
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
        
        pygame.displayflip()
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

def deal_cards_with_animation(screen, deck, player, computer, deck_pos, card_back, draw_frame_cb, spacing = 30):
    for i in range(7):
        card = deck.pop()  #logic based function covers these
        player.hand.append(card)

        end_pos = (100 + i * spacing, 500)
        animate_card(screen, card.image, deck_pos, end_pos, draw_frame_cb)

        card = deck.pop()
        computer.hand.append(card)

        end_pos = (100 + i * spacing, 50)
        animate_card(screen, card_back, deck_pos, end_pos, draw_frame_cb)

def main():
    #game setup
    pygame.init()
    screen = pygame.display.set_mode((900, 650))
    pygame.display.set_caption("Welcome to UNO with the computer!!!")
    clock = pygame.time.Clock()

    #scenery. Colors for the background
    TABLE_GREEN = (34, 139, 34)

    #images
    card_back_surf = load_image_by_name("card back", size=(980, 120)) or pygame.Surface((80,120))
    shared_deck_surf = load_image_by_name("shared_deck", size=(80, 120)) or card_back_surf
    
    deck = generate_deck()
    player = Player("you", is_human=True)
    computer = Player("Python", is_human=False)

    shared_pos = (400, 260)
    #draw the frame
    def draw_frame(surf):
        surf.fill(TABLE_GREEN)
        surf.blit(shared_deck_surf, (shared_pos[0]-120, shared_pos[1]-20))  #deck, left of center
        surf.blit(surf, pile, center=(shared_pos[0], shared_pos[1]))
        draw_pile(surf, pile, center=(shared_pos[0], shared_pos[1]))
        
        draw_hand(surf, player.hand, 50, 500, 30, card_back_surf, show_face=True)
        draw_hand(surf, computer.hand, 50, 50, 30, card_back_surf, show_face=False)

    deal_cards_animation(screen, deck, player, computer, card_back_surf, (shared_pos[0]-120, shared_pos[1]-20), player_start_pos=(shared_pos[0], shared_pos[1]), computer_start_pos=(shared_pos[0], shared_pos[1]), draw_frame_cb=draw_frame, card_spacing=30)
    if deck:
        pile.append(deck.pop())
    
    running = True
    turn = 0
    pending_draw = 0
    while running:
        draw_frame(screen)#set the game up
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            #player's turn
            if turn%2 == 0: 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos 
                    rects = draw_hand(screen, player.hand, 50, 500, 30, card_back_surf, show_face=True)
                    for idx, r in enumerate(rects):
                        if r.collidepoint(mouse_pos):
                            chosen = player.hand[idx]
                            top = pile[-1] if pile else None 

                            if (pending_draw > 0 and is_valid_stack(chosen, top, pending_draw)) or (pending_draw=0 and chosen.is_match(top)):
                                player.hand.pop(idx)
                                pile.append(chosen)

                                pending_draw = apply_special_card_effects(chosen, turn, pending_draw) or pending_draw   #update the pending draw and turn
                                turn += 1
                            else:
                                print("Invalid move")
            else:
                pygame.time.delay(400)
                top = pile[-1] if pile else None 
                played = False 
                for c in computer.hand:
                    if pending_draw == 0 and c.value not in ["+2", "+4"] and c.is_match(top):
                        computer.hand.remove(c) #remove card
                        pending_draw = apply_special_card_effects(c, turn, pending_draw) or pending_draw
                        played = True 
                        beak 
                        
                if not played and pending_draw>0:
                    for c in computer.hand:
                        if is_valid_stack(c, top, pending_draw):
                            computer.hand.remove(c)
                            pile.append(c)
                            pending_draw = apply_special_card_effects(c, turn, pending_draw) or pending_draw
                            played = True 
                            break 
                
                if not played:
                    draw_until_playable(computer, pile, deck, turn, pending_draw)
                turn += 1
        w, uno = player.valid_win()
        if w:
            print("you won!")
            running = False     #break the loop b/c player won
            break 

        w2, uno = computer.valid_win()
        if w:
            print("Computer won")
            running = False
            break 
    pygame.quit()

if __name__ == "__main__":
    main()

