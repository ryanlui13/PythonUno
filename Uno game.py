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

    deal_cards_with_animation(screen, deck, player, computer, card_back_surf, (shared_pos[0]-120, shared_pos[1]-20), draw_frame, player_start_pos=(shared_pos[0], shared_pos[1]), computer_start_pos=(shared_pos[0], shared_pos[1]), card_spacing=30)
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
        "catch": catch_rect
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
            draw_button(screen, buttons["comp_first"], "computers first!", font, (120, 0, 255), (255, 255, 255))
        elif game_state == "choosing_color":
            return draw_color_buttons(screen, font)
        elif game_state == "wait_for_uno":
            draw_button(screen, buttons["uno"] , "UNO!", font, (255, 0, 0), (255, 255, 255))
            draw_button(screen, buttons["catch"], "CATCH!", font, (0, 0, 0), (255, 255, 255))
        elif game_state == "game_over":
            restart_rect = pygame.Rect(350, 300, 200, 60)
            draw_button(screen, buttons["restart"], "Restart game", font, (0, 0, 0), (255, 255, 255))
            return {"restart": restart_rect}
        
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
                running = False

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
                    if restart_rect.collidepoint(mx, my):
                        main()  #restart game loop

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
                            running = False 
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
            
            status_comp = computer.valid_win()
            if status_comp == "win":
                game_message = "Computer won"
                game_state = "game_over"
                break 
    pygame.quit()

if __name__ == "__main__":
    main()
