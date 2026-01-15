Python UNO 
A fully functional, 2 player uno game built with Python and pygame package. This game uses a state-driven game engine, automated computer logic and an executable distribution. 

🚀 Key Features
1) Intelligent Computer AI: The computer opponent uses logic heuristics to choose the best color (for wild and +4 cards) and stack penalty cards.
2) State-Driven Game Loop: Managed complex game transitions including turn-taking, color selection, and "UNO" declaration phases.
3) Penalty Stacking: Supports stacking mechanics for +2 and +4 cards, increasing the "Pending Draw" pool. This is a normal rule for playing uno
4) Standalone Distribution: Packaged into a portable .exe using PyInstaller. All assets are grouped togeher for easy play.
5) Used the OS module for cross-platform path management and asset validation. 

🛠️ Technical Challenges & Solutions
1) The turn-logic was refactored numerous times. Initially, the turn-handling was intertwined with the special card effects (+2, +4...), leading to logic errors. I refactored the engine to use a state machine that uses turn-increments in the main event loop. This allowes penalty stacking to be stable.
2) Initally the game engine struggled with "ghost clicks" (playing a card automatically triggers changing the current turn) before the UI could update itself. Other times the computer would play multiple cards in a single frame (not following valid uno rules). I used a state machine to gate inputs. I separated the game into different states (playing, choosing_color and wait_for_uno). this ensures the mouse clicks were processed for the active player's hand and the computer's logic is only triggered when the state was explicitly set to its turn. 
3) when a wild card was played, the top card on the pile would revert to a default white rectangle because the card object's color property was updated. this caused the image surface to not be re-mapped to the new color. I updated choosing_color to update the card on the pile. 


🛠️ Built With
Language: Python
Library: Pygame
Deployment: PyInstaller
