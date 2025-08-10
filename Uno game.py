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

def animate_cards(start_x, start_y, end_x, end_y):
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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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


#rules of the game
#stack same number or color of previous card
turn = 0
player1 = True
player2 = False #python's turn 
win = False 
while win != True:
    #if player 1 has 0 cards:
        win = True
    #if player 1 has 0 cards:
        win = True
    turn += 1
    if turn % 2 == 0:
        player1 = True 
        #player 1 places card down
        if player1_card == skip or player2_card == reverse:
            turn = turn + 2
    if turn%2 == 1:
        player2 = True 
        if player2_card == skip or player2_card == reverse:
            turn = turn + 2
        #player 2 places card down
      
#skip = skip next turn
#reverse = change direction

#plus2 (any color)
#if next player has plus2, it can be stacked
#if next player has plu4, it can be stacked
    #player who put plus4 down picks the color. puts a card w/ that color down

#draw new cards until the player gets the same number or color
#put new card down 

#when there's only 1 card left: type "UNO!"