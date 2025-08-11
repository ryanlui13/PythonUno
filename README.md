import pygame
import os 
import random 

pygame.init()

#class to upload ALL cards
class Card():
    def __init__(self, color, value):   #initalize card and their images
        self.color = color
        self.value = value 
        self.image = self.load_image()

    def load_image(self):   #load the images
        base_name = f"{self.color}_{self.value}" if self.color else self.value 
        possible_extensions = [".png", ".jpg"]
        for extension in possible_extensions:
            path = os.path.join("cards", base_name + extension)
            if os.path.exists(path):
                image = pygame.image.load(path)
                return pygame.transform.scale(image, (100, 150))
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
        random.choice(colors)
        random.choice(values)
        for value in values[1:9]:
            deck.append(Card(color, value))
            deck.append(Card(color, value))
    
    for wild in wilds:
        for _ in range(4):
            deck.append(Card(None, wild))
    
    return deck 

def shuffle_deck(deck): #shuffle deck before new game 
    random.shuffle(deck) 

def distribute_cards(deck, num_players=2): #pass 7 cards to players
    hands = [[] for _ in range(num_players)]
    for i in range(7):
        for hand in hands:
            hand.append(deck.pop())
    return hands 

def player_turn(player_deck, card_rects, pile, mouse_pos):  #check if the move is valid. Stacking and card rules
    for i, rect in enumerate(card_rects):   #click on the card
        if rect.collidepoint(mouse_pos):
            chosen_Card = player1_deck[i]
        
        top_card = pile[-1]
        if Card.is_match(chosen_Card, top_card):
            pile.append(player_deck.pop(i))

            if chosen_Card.value == "skip":
                turn += 2
            
            elif chosen_Card.value == "reverse":
                turn -= 1
            
            elif chosen_Card.value == "+2": #+2 rules
                draw_penalty = 2
                if any(card.value in ("+2", "+4") for card in computer_deck):
                    chosen_index = None
                    for i, card in enumerate(computer_deck):
                        chosen_index = i
                        break 
                    if chosen_index is not None:    #choose the right card to stack
                        pile.append(computer_deck.pop(chosen_index))
                        if card.value in "+2":  #+2 added
                            draw_penalty += 2
                            for _ in range(2):
                                player1_deck.append(pile.pop())
                        if card.value in "+4":
                            draw_penalty += 4
                            for _ in range(4):  #+4 added
                                player1_deck.append(pile.pop())
                            choosen_color = max(["red", "yellow", "green", "blue"], key=lambda c:sum(1 for x in computer_deck if x.color == c))
                            current_color = choosen_color 
                        else:   #if the computer DOES NOT have a valid +2 or +42 wild card
                            for _ in range(draw_penalty):
                                computer_deck.append(pile.pop())


            elif chosen_Card.value == "+4": #wild card rules
                draw_penalty = 4

                choosen_index = None 
                for i, card in enumerate(computer_deck):
                    if chosen_Card.value == "+4":
                        choosen_index = i
                        break 
                
                if choosen_index is not None:
                    pile.append(computer_deck.pop(choosen_index))
                    draw_penalty += 4 
                    choosen_color = max(
                        ["red", "yellow", "green", "blue"],
                        key = lambda c:sum(1 for x in computer_deck if x.color == c)
                    )
                    current_color = choosen_color 
                else:
                    for _ in range(draw_penalty):                    
                        computer_deck.append(pile.pop())
                
                print("Choose red, yellow, green or blue: ")
                new_color = input(" >").strip().lower()
                chosen_Card.color = new_color 
                current_color = new_color 

                if any(card.value in "+4" for card in computer_deck):
                    chosen_index = None 
                    for i, card in enumerate(computer_deck):
                        chosen_index = i 
                        break 
                    if chosen_index is not None:
                        pile.append(computer_deck.pop(chosen_index))
                        draw_penalty += 4
                        for _ in range(draw_penalty):
                            computer_deck.append(pile.pop())
                        choosen_color = max(["red", "yellow", "green", "blue"], key=lambda c:sum(1 for x in computer_deck if x.color == c))
                        current_color = choosen_color 
                    else: 
                        for _ in range(draw_penalty):
                            computer_deck.append(pile.pop())
                
                print("Choose red, yellow, green or blue: ")
                new_color = input("> ").strip().lower()
                chosen_Card.color = new_color 

            return "played"
        
        else:   #while the card does NOT match, wait for a valid card
            print("Choose a card with the same color or Value")
            return None 
    return None 
    
    #choose card that matches
    choosen_card = player_deck

def computer_turn(player_deck, card_rects, pile):   #computer's turn f(x)
    pass 

def start_stack_selection(first_index, chosen_value):   #find the stack
    return {
        "active": True,
        "value": chosen_value,
        "selected_indices": [first_index],
    }

def add_to_stack(stack_state, index, player_deck):  #add cards to the stack
    if not stack_state or not stack_state["active"]:    #index to stack selection
        return False 
    
    if 0 <= index < len(player_deck) and player_deck[index].value == stack_state[index].value:  #make sure the chosen card has the same value
        if index not in stack_state["selected_indices"]:    #nothing is duplicated to the pile twice
            stack_state["selected_indices"].append(index)
        return True 
    return False 

def finalize_stack(stack_state, player_deck, pile): #stack in the order the player chose
    if not stack_state or not stack_state["active"]:
        return None 
    
    selected_indices = stack_state["selected_indices"]
    selected_cards = [player1_deck[idx] for idx in selected_indices]    #choose the cards

    for idx in sorted(selected_indices, reverse=True):
        player1_deck.pop(idx)   #remove the chosen cards

    for card in selected_cards:
        pile.append(card) 
    
    return selected_cards[-1] if selected_cards else None

def no_stack(stack_state):  #no stack is made
    return None  

def check_win(player_hand):    #check if a player has 0 cards
    if len(player_hand) == 0:
        return True 

def valid_win(player, player_hand, is_human=True, player_status=None):
    #player is a string. Show either Player's name or Computer (if that's the player)
    if player_status is None:
        player_state = {}
    
    if len(player_hand) > 1:    #reset declared uno to false if they have more than 1 card
        player_status['declared_uno'] = False 
        return False, False #return false => they DIDN'T win, NO uno 

    if len(player_hand) == 0:   #check if the player has no cards left
        return True, False    #they DID WIN, NO uno!
    
    if len(player_hand) == 1:
        if player_status.get('declared_uno', False):    #check if uno was declared. valid ONLY if declared
            player_hand += 2
            return False, True  #they didn't win, BUT they HAVE UNO
    
        if is_human:
            resp = input(f"{player}, you have 1 card left. Type 'Uno' to declare Uno: ").strip().lower()
            if resp.lower() == "uno":
                player_state['declared_uno'] = True #if they say Uno, declared is True
                print("You declared UNO! Valid!")
                return False, True #DIDN'T win, but declared uno
        else:
            print(f"{player} said: UNO!")
            player_status['declared_uno'] = True 
            return False, True 
    
    return False, False 

def animate_cards(start_x, start_y, end_x, end_y):  #graphics
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

#game
#game set up
print("Welcome to UNO with the computer!!!")
pygame.init()
screen = pygame.display.set_mode(800, 600)
pygame.display.set_caption("Uno card dealing")

#scenery 
TABLE_GREEN = (0, 100, 0)
deck_x, deck_y = 350, 225
player1_y = 540
computer_y = 50 

#drawing pile
sharedDeck_img = pygame.image.load("shared_deck.png")
sharedDeck_img = pygame.transform.scale(sharedDeck_img, (100, 150))

#drawing card to player
cardBack_img = pygame.image.load("card_back.png")
cardBack_img = pygame.transform.scale(cardBack_img, (100, 150))

#place holder deck => update when the annimation works 
colors = ["red", "green", "blue", "yellow"]
values = ["0","1","2","3", "4", "5", "6", "7", "8", "9", "+2"]
wilds = "plus4"
deck = [(color, value) for color in colors for value in values for _ in range(2)]
random.shuffle(deck)

player1_hand = []
computer_hand = []

running = True 
cards_per_player = 7
player1_deck = distribute_cards(player1_hand)
computer_deck = distribute_cards(computer_hand)

pile = []

turn = 0
resp = input("Do you want to go first or should the computer go first? Type me if you want to go: ")
if resp == "me":
    player1_turn = True
    print("Your turn!")
else:
    computer_turn = True
    print("Computer starts now")

while running:
    card_rects = []
    for index, card in enumerate(player1_deck):
        rect = card.image.get(topleft=(50+index * 30, 500))
        screen.blit(card.image, rect)
        card_rects.append(rect)
    
    for index, card in enumerate(computer_deck):
        rect = card.image.get(topright=(50+index * 30, 500))
        screen.blit(card.image,rect)
        card_rects.append(rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if stack_state and stack_state.get("active", False):
                for idx, rect in enumerate(card_rects):
                    if rect.collidepoint(mouse_pos):
                        added = add_to_stack(stack_state, idx, player1_deck) 
                        if not added:
                            print("Add a valid card.")
                        else: 
                            print(f"ADDED {player1_deck[idx].color} {player1_deck[idx].value} to stack preview") 
            
            else:
                for idx, rect in enumerate(card_rects):
                    if rect.collidepoint(mouse_pos):
                        clicked_card = player1_deck[idx]
                        top = pile[-1] 
                    
                    if Card.is_match(clicked_card, top):
                        matches = [(i, c) for i,c in enumerate(player1_deck) if c.value == clicked_card.value]
                        if len(matches) > 1:
                            stack_state = start_stack_selection(idx, clicked_card.value)    #start stacking same value cards
                            print("Stack mode: click other matching-value cards in the order you want them to be in the pile. Last card will determine next player's move! Enter to confirm. Esc to cancel!")
                        else: 
                            pile.append(player1_deck.pop(idx))
                            last_card = pile[-1]
                            player1_plays = player_turn(player1_deck, card_rects, pile, mouse_pos)
                    else: 
                        print("Invalid move!")
                    break #stop checking rects

        elif event.type == pygame.KEYDOWN:  #add the stacked card to the pile. 
            if stack_state and stack_state.get("active", False):
                if event.key == pygame.K_RETURN:
                    if event.key == pygame.K_RETURN:
                        last_card = finalize_stack(stack_state, player1_deck, pile)
                        stack_state = None 
                        if last_card:
                            print(f"played stacked {last_card.value}")
                    elif event.key = pygame.K_ESCAPE:
                        stack_state = None
                        print("Canceled stacking!")
        

        if turn%2 == 0 and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos 
            for i, rect in enumerate(card_rects):
                if rect.collidepoint(mouse_pos):
                    chosen_Card = player1_deck[i]

                    if Card.is_match(chosen_Card, pile[-1]):
                        pile.append(player1_deck.pop(i))

                        if chosen_Card.value in ("skip"):       #skip and reverse
                            turn += 2
                        elif chosen_Card.value in ("reverse"):
                            turn -= 1
                        elif chosen_Card.value == "+2": #fix this
                            draw_penalty = 2
                            if "+2" or "+4" in computer_deck.value:
                                pile.append(computer_deck.pop(i)) 
                            
                            for c in range(2):
                                computer_deck.append(pile.pop())
                            turn += 1
                        elif chosen_Card.value == "+4": #fix this
                            for c in range(4):
                                computer_deck.append(pile.pop())
                            turn += 1
                    else:
                        print("Pick a card w/ same color or value!")
    
        if turn%2 == 1: #computer turn (AI)
            played = False 
            for i, card in enumerate(computer_deck):
                if Card.is_match(card, pile[-1]):
                    pile.append(computer_deck.pop(i))
                    played = True 
                    
                    if card.value in ("skip"):
                        turn += 2
                    elif card.value in ("reverse"):
                        turn -= 1    
                    elif card.value == "+2":    #fix this
                        draw_penalty = 2
                        for c in range(2):
                            player1_deck.append(pile.pop())
                        turn += 1

                    elif card.value == "+4":    #fix this
                        draw_penalty = 4
                        for c in range(draw_penalty):
                            player1_deck.append(pile.pop())
                        
                        colors = ["red", "yellow", "green", "blue"]
                        color_counts = {c: 0 for c in colors}
                        for c in computer_deck:
                            if c.color in colors:
                                color_counts[c.color] += 1
                        choosen_color = max(color_counts, key=color_counts.get)
                        print(f"The new color is {choosen_color}")

                        user_plays = any(card.color == choosen_color for card in player1_deck)
                        while not user_plays:
                            print("Draw a card...")
                            player1_deck.append(pile.pop())
                            user_plays = any(card.color == choosen_color for card in player1_deck)
                        turn +=1

                    else:    
                        turn +=1

            if not played:
                if Card.is_match(card, pile[-1]) == False:
                    computer_deck.append(pile.pop())
                    turn += 1
    
        #check for a win for EACH user    
        if len(player1_hand) == 1:
            valid_win(player1, player1_deck, )

    #background 
    screen.fill(TABLE_GREEN)
    screen.blit(sharedDeck_img, (deck_x, deck_y))

    for card_num in range(cards_per_player):
        animate_cards(deck_x, deck_y, 100 + len(player1_hand) * 30, player1_y)
        player1_hand.append(deck.pop()) #add the drawed cards to the player's hand

        animate_cards(deck_x, deck_y, 100 + len(computer_hand) * 30, computer_y)
        computer_hand.append(deck.pop())    #add to computer's hand 

    for i, _ in enumerate(player1_hand):    #draw cards
        screen.blit(cardBack_img, (100 + i * 30, player1_y))
    
    for i, _ in enumerate(computer_hand):   #draw cards for computer
        screen.blit(cardBack_img, (100 + i * 30, computer_y)) 
    
    pygame.display.flip()
