import random
from poker_helpers import PLAYER_ROLES, create_deck, deal_card, hand_rank, best_hand, Player

class Game:
    def __init__(self, players, starting_chips):
        self.deck = create_deck()  # Create and shuffle a deck of cards
        random.shuffle(self.deck)
        self.players = [Player(name, starting_chips) for name in players]  # Initialize players
        self.community_cards = []  # List to hold community cards
        self.pot = 0  # The total amount of chips in the pot
        self.current_bet = 0  # The current highest bet
        self.winner = None  # The winner of the game

    def assign_roles(self):
        """Assign roles to players (Dealer, Small Blind, Big Blind)."""
        for player, role in zip(self.players, PLAYER_ROLES):
            player.role = role

    def deal_to_players(self):
        """Deals two cards to each player."""
        for _ in range(2):
            for player in self.players:
                player.receive_card(deal_card(self.deck))

    def deal_community_card(self):
        """Deals a single community card."""
        self.community_cards.append(deal_card(self.deck))

    def take_bets(self):
        """Handles a round of betting."""
        for player in self.players:
            bet = min(player.chips, self.current_bet)  # Simplified betting logic
            player.place_bet(bet, self)
            self.pot += bet

    def play_round(self):
        """Plays a full round of Texas Hold'em (simplified)."""
        self.deal_to_players()
        self.take_bets()

        # Flop (deal three community cards)
        for _ in range(3):
            self.deal_community_card()
        self.take_bets()

        # Turn (deal one community card)
        self.deal_community_card()
        self.take_bets()

        # River (deal one community card)
        self.deal_community_card()
        self.take_bets()

        # Showdown to determine the winner
        self.showdown()

    def showdown(self):
        """Determine the winner (simplified)."""
        # Evaluate the best hand for each active player
        player_hands = [(player, best_hand(player.hand, self.community_cards)) for player in self.players if player.is_active]
        if len(player_hands) == 0:
            print("All players have folded. No winner.")
            return
        winner = max(player_hands, key=lambda x: hand_rank(x[1]))[0]  # Find the player with the best hand
        print(f"The winner is {winner.name} with hand {winner.hand}")
        for player in self.players:
            print(f"{player.name} has {player.hand} with community cards {self.community_cards}")
        print(f"The pot is {self.pot} chips.")
        self.winner = winner

# Example usage:
players = ['Alice', 'Bob', 'Charlie']
game = Game(players, starting_chips=1000)
game.play_round()
