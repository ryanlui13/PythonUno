import os 
import pygame 
import random 

pygame.init()

if not pygame.font:
    print("Font disabled")
if not pygame.mixer:
    print("Sound disabled ")

from collections import Counter 

#class for ALL card properties 
class Card():
    def __init__(self, color, value):   #initalize card and their images
        self.color = color
        self.value = value 
        self.image = self.load_image()

    def load_image(self):   #load the images
        base_name = f"{self.color}_{self.value}" 
        if self.color != "wild":    #normal cards
            base_name = f"{self.color}_{self.value}" 
        else:    #wild card value exception for +4 and plain wild
            base_name = f"wild_{self.value}"

        #both file types
        possible_extensions = [".png", ".jpg"]
        for extension in possible_extensions:
            path = os.path.join("images", base_name + extension)
            if os.path.exists(path):
                return  pygame.image.load(path)

        print(f"Image not found for {base_name}")
        return None 

    def draw(self, screen, x, y):   #draw cards for the player 
        screen.blit(self.image, (x, y))
    
    def is_match(self, other_card): #check if the player's card can be placed down
        if self.color == other_card.color:
            return True 
        if self.value == other_card.value:
            return True 
        return False
    
    def __str__(self):  #what the user sees
        return f"{self.color} {self.value}" if self.color else self.value

def generate_deck():    #random deck for the player 
    colors = ["red", "yellow", "green", "blue"]
    values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "skip", "reverse", "+2"]
    wilds = ["wild", "+4"]
    
    deck = []
    for color in colors:
        for value in values[0:9]:
            deck.append(Card(color, value))
            if value != 0:
                deck.append(Card(color, value))
    
    for _ in range(4):
        deck.append(Card("wild", "+4"))
        deck.append(Card("wild", "wild"))
    
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

def distribute_cards(hand, num_players=2): #pass 7 cards to players
    deck = generate_deck() #build the deck
    shuffle_deck(deck)   #shuffle 
    for _ in range(num_players):
        if deck:
            hand.append(deck.pop())
        else:
            print("Deck is empty. Can't deal more cards!")

    return hand

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

def draw_until_playable(player_hand, pile, deck, turn, pending_draw, max_draws=50):   #keep drawing cards until a match is found
    draws = 0
    top_card = pile[-1]

    while True:
        for card in list(player_hand):
            if (pending_draw > 0 and is_valid_stack(card, top_card, pending_draw)) or (pending_draw == 0 and Card.is_match(card, top_card)):
                player_hand.remove(card)
                pile.append(card)
                return apply_special_card_effects(card, turn, pending_draw)
        
        if draws >= max_draws:  #limit to drawing
            print("Max drawing limit reached! Next player's turn")
            break 
        
        if len(deck) == 0:
            print("Deck empty. Reshuffling now...")
            top_card = pile.pop()
            deck.extend(pile)
            pile.clear()
            random.shuffle(deck) 
        
        drawn_card = deck.pop()
        player_hand.append(drawn_card)
        draws+=1 
        print("New card was drawn: {drawn_card}") 

        if (pending_draw > 0 and is_valid_stack(drawn_card, top_card, pending_draw)) or pending_draw == 0 and Card.is_match(drawn_card, top_card):
            player_hand.remove(drawn_card)
            pile.append(drawn_card)                                                                         
            return apply_special_card_effects(drawn_card, turn, pending_draw=0)

def check_win(player_hand):    #check if a player has 0 cards
    if len(player_hand) == 0:
        return True 

def valid_win(player, player_hand, is_human=True, player_status=None):
    #player is a string. Show either Player's name or Computer (if that's the player)
    if player_status is None:
        player_status = {"declared_uno": False}
    
    if len(player_hand) > 1:    #reset declared uno to false if they have more than 1 card
        player_status['declared_uno'] = False 
        return False, False #return false => they DIDN'T win, NO uno 

    if len(player_hand) == 0:   #check if the player has no cards left
        return True, False    #they DID WIN, NO uno!
    
    if len(player_hand) == 1:
        if player_status.get('declared_uno', False):    #check if uno was declared. valid ONLY if declared
            player_hand.extend[(deck.pop(), deck.pop())]
            return False, True  #they didn't win, BUT they HAVE UNO
    
        if is_human:
            resp = input(f"{player}, you have 1 card left. Type 'Uno' to declare Uno: ").strip().lower()
            if resp.lower() == "uno":
                player_status['declared_uno'] = True #if they say Uno, declared is True
                print("You declared UNO! Valid!")
                return False, True #DIDN'T win, but declared uno
            else:
                player_status['declared_uno'] = False 
                print("you forgot to declare Uno. Pick up 2 cards! ...")
                player_hand.extend([deck.pop(), deck.pop()])
                return False, False 
        else:   
            #computer portion 
            print(f"{player} said: UNO!")
            player_status['declared_uno'] = True 
            return False, True 
    
    return False, False 

def animate_cards(screen, start_x, start_y, end_x, end_y, cardBack_img, TABLE_GREEN, deck_x, deck_y):  #graphics
    steps = 20
    for i in range(steps):
        t = i / steps 
        new_x = start_x + (end_x - start_x) * t
        new_y = start_y + (end_y - start_y) * t
        screen.fill(TABLE_GREEN)
        screen.blit(sharedDeck_img, (deck_x, deck_y))
        screen.blit(cardBack_img, (new_x, new_y))
        pygame.display.flip()
        pygame.time.delay(15)

def main():
    #game setup
    pygame.init()
    pygame.display.set_caption("Welcome to UNO with the computer!!!")
    clock = pygame.time.Clock()

    #scenery. Colors for the background
    TABLE_GREEN = (34, 139, 34)

    #images
    sharedDeck_img = pygame.image.load("images/card_back_img.png")
    sharedDeck_img = pygame.transform.scale(sharedDeck_img, (80, 120))

    deck = generate_deck()
    random.shuffle(deck) 

    #place the deck in the middle
    deck_x, deck_y = 350, 225
    pile_x, pile_y = 500, 250 

    player1_deck = []
    computer_deck = []
    pile = []

    #distribute cards
    for i in range(7):
        card = deck.pop()
        player1_deck.append(card)
        animate_cards(screen, deck_x, deck_y, 50 + i * 30, 500, card.image, sharedDeck_img, TABLE_GREEN, deck_x, deck_y)

        card = deck.pop()
        computer_deck.append(card)
        animate_cards(screen, deck_x, deck_y, 50 + i * 30, 50, card.image,sharedDeck_img, TABLE_GREEN, deck_x, deck_y)

    pile.append(deck.pop())

    running = True 

    turn = 0
    num_players = 2
    first_player = input("Do you want to go first or should the computer go first? Type yes if you want to go: ")
    if first_player == "yes":
        player1_turn = True 
        print("Your turn!")
    else:
        turn = 1
        player1_turn = False 
        print("Computer starts now")

    while running:
        screen.fill(TABLE_GREEN)
        
        card_rects = [] #reset after EVERY turn

        for index, card in enumerate(player1_deck): #draw player 1 deck
            x = 50 + index*30
            y = 500 
            card_image = card_image.get(str(card),  None) 
            if card_image:
                screen.blit(card_image, (x,y))
            
            rect = pygame.Rect(x, y, 80, 120)
            card_rects.append((rect, card))
        
        for index, card in enumerate(computer_deck):    #draw computer deck
            x = 50 + index * 30
            y = 50 
            screen.blit(card_back_img, (x, y))

        if pile:    #draw the pile
            top_card = pile[-1]
            top_rect = top_card.image.rect(center=(400, 300))
            screen.blit(top_card.image, top_rect)
        
        check_deck(deck)
        
        if turn == 0:
            print("\nYour turn!")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            #player's turn
            if turn%num_players == 0: 
                 #player have uno?
            
                win, uno = valid_win("You", player1_deck, is_human=True, player_status=player_status)
                if win:
                    print("You won UNO!")
                    running = False 
                    break 
                
                if len(player1_deck) == 1 and not uno:
                    print("You forgot to declare Uno. Draw 2 cards. ")
                    player1_deck.extend([deck.pop(), deck.pop()])
                
                #computer have uno?
                win, uno = valid_win("Python", computer_deck, is_human=False, player_status=None)
                if win:
                    print("Computer won!")
                    running = False
                    break 
                if len(computer_deck) == 1 and not uno:
                    print("Computer forgot to declare uno.")
                    computer_deck.extend([deck.pop(), deck.pop()])

                if event.type == pygame.QUIT:   #quit game
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:    #start the game 
                    mouse_pos = event.pos 
            
                    for idx, rect in enumerate(card_rects): #player cards
                        if rect.collidepoint(mouse_pos):    #event 
                            choosen_card = player1_deck[idx]
                            top_card = pile[-1]

                            if pending_draw > 0:
                                if is_valid_stack(choosen_card, top_card, pending_draw):
                                    pile.append(player1_deck.pop(idx))  #add the choosen card to the pile
                                    pending_draw += card_penalty_value(choosen_card)    #draw cards based on penalty value
                                    print("Stacked! Draw {pending_draw} cards")
                                else:
                                    print("Invalid stack. Drawing cards now...")
                                    draw_until_playable(player1_deck, pile, deck, turn, pending_draw)
                                    pending_draw = 0
                            
                            else: 
                            #normal stack 
                                if Card.is_match(choosen_card, top_card):
                                    pile.append(player1_deck.pop(idx))
                                    pending_draw = apply_special_card_effects(card, turn, pending_draw)
                                else: 
                                    print("Invalid. Choose a card w/ the same color or value! ")
                turn += 1        
            else: 
                #player have uno?
                win, uno = valid_win("You", player1_deck, is_human=True, player_status=player_status)
                if win:
                    print("You won UNO!")
                    running = False 
                    break 
                if len(player1_deck) == 1 and not uno:
                    print("You forgot to declare Uno. Draw 2 cards. ")
                    player1_deck.extend([deck.pop(), deck.pop()])
                
                #computer have uno?
                win, uno = valid_win("Python", computer_deck, is_human=False, player_status=None)
                if win:
                    print("Computer won!")
                    running = False
                    break 
                if len(computer_deck) == 1 and not uno:
                    print("Computer forgot to declare uno.")
                    computer_deck.extend([deck.pop(), deck.pop()])
                
                #computer's turn
                pygame.time.delay(500)  #pause for suspense and realism 
                playable = []
                top_card = pile[-1]

                #strategy => save the +2 and +4 for later. ONLY place a +2 when needed. 
                if pending_draw > 0:
                    for c in computer_deck: #loop through deck for penalty cards
                        if is_valid_stack(c, top_card, pending_draw):
                            choosen_card = c 
                            break 
                    
                    if choosen_card:
                        pile.append(computer_deck.pop(choosen_card))
                        pending_draw = apply_special_card_effects(choosen_card, turn, pending_draw)
                    else:
                        print("Computer can't stack. Drawing cards now...")
                        pending_draw = 0
                else:
                    #no penalty for computer
                    for c in computer_deck:
                        if Card.is_match(c, top_card):
                            if c.value not in ["+2", "+4"]: #save the penalty card unless needed
                                choosen_card = c
                                break 
                            
                    if not choosen_card:
                            for c in computer_deck:
                                if Card.is_match(c, top_card) and c.value == "+2":  #save +2
                                    choosen_card = c
                                    break 

                                if Card.is_match(c, top_card) and c.value == "+4":  #save +4
                                    choosen_card = c 
                                    break 
                    
                    if choosen_card:
                        computer_deck.remove(choosen_card)
                        pile.append(choosen_card)
                        pending_draw = apply_special_card_effects(choosen_card, turn, pending_draw)
                    else:
                        draw_until_playable(computer_deck, pile, deck) 

                turn += 1

        pygame.display.flip() 

if __name__ == "__main__":
    main()
