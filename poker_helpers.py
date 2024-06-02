from itertools import combinations

# Define constants for suits and ranks in a standard deck of cards
SUITS = '♠ ♥ ♦ ♣'.split()
RANKS = '2 3 4 5 6 7 8 9 10 J Q K A'.split()

# Define player roles in a poker game
PLAYER_ROLES = ['Dealer', 'Small Blind', 'Big Blind']

# Utility functions

def create_deck():
    """Creates a standard deck of 52 cards."""
    return [(rank, suit) for suit in SUITS for rank in RANKS]

def deal_card(deck):
    """Deals a single card from the deck."""
    return deck.pop()

def hand_rank(hand):
    """Evaluates the rank of a hand (sophisticated version)."""
    rank_values = {r: i for i, r in enumerate(RANKS, start=2)}
    ranks = sorted((rank_values[rank] for rank, suit in hand), reverse=True)
    suits = [suit for rank, suit in hand]

    # Check for flush and straight
    is_flush = len(set(suits)) == 1
    is_straight = len(set(ranks)) == 5 and max(ranks) - min(ranks) == 4

    # Special case for Ace-low straight (5-high straight)
    if ranks == [14, 5, 4, 3, 2]:
        is_straight = True
        ranks = [5, 4, 3, 2, 1]

    def kind(n, ranks):
        """Returns the first rank that appears exactly n times in the hand."""
        for rank in ranks:
            if ranks.count(rank) == n:
                return rank
        return None

    def two_pair(ranks):
        """Returns two pairs if present, otherwise None."""
        pair1 = kind(2, ranks)
        pair2 = kind(2, list(reversed(ranks)))
        if pair1 and pair2 and pair1 != pair2:
            return (pair1, pair2)
        return None

    # Determine hand ranking
    if is_straight and is_flush:
        return (8, max(ranks))  # Straight flush
    if kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))  # Four of a kind
    if kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))  # Full house
    if is_flush:
        return (5, ranks)  # Flush
    if is_straight:
        return (4, max(ranks))  # Straight
    if kind(3, ranks):
        return (3, kind(3, ranks), ranks)  # Three of a kind
    if two_pair(ranks):
        return (2, two_pair(ranks), ranks)  # Two pair
    if kind(2, ranks):
        return (1, kind(2, ranks), ranks)  # One pair
    return (0, ranks)  # High card

def best_hand(player_hand, community_cards):
    """Determines the best hand from the player's cards and community cards."""
    all_cards = player_hand + community_cards
    best = max(combinations(all_cards, 5), key=hand_rank)
    return best

class Player:
    def __init__(self, name, chips):
        self.name = name  # Player's name
        self.chips = chips  # Amount of chips the player has
        self.hand = []  # Player's current hand
        self.bet = 0  # Current bet amount
        self.role = None  # Player's role in the game (Dealer, Small Blind, Big Blind)
        self.is_active = True  # Whether the player is still active in the game

    def receive_card(self, card):
        """Adds a card to the player's hand."""
        self.hand.append(card)

    def place_bet(self, amount, game):
        """Places a bet and updates the player's chips and bet amount."""
        if amount > self.chips:
            game.errors.append(f"{self.name} doesn't have enough chips to bet {amount}.")
            # raise ValueError(f"{self.name} doesn't have enough chips to bet {amount}.")
            amount = self.chips
        self.chips -= amount
        self.bet += amount
