import random
import pickle
import glob
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

from poker_helpers import PLAYER_ROLES, create_deck, deal_card, hand_rank, best_hand, Player

# Load environment variables
load_dotenv()

# Define response schemas for structured output
response_schemas = [
    ResponseSchema(name="betting_decision", description="Player's betting decision. Possible values: Fold, Call, Raise, Check."),
    ResponseSchema(name="raise_amount", description="Amount to raise the current bet in case of Raise. The value is ignored for other decisions. The player must have enough chips to call or raise."),
    ResponseSchema(name="explanation", description="Explanation of the player's decision."),
]

# Initialize output parser from response schemas
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = output_parser.get_format_instructions()

class OpenAIPlayer(Player):
    def __init__(self, name, model, chips):
        self.llm = ChatOpenAI(model=model)
        self.model_name = model
        # Create an agent executor by passing in the agent and tools
        super().__init__(name, chips)

    def place_bet(self, game):
        """Use OpenAI model to decide and place a bet."""
        betting_prompt = """
            You are a poker agent playing Texas Hold'em.

            Assess the current situation and decide what kind of bet to make.

            Your current properties are:
            - Chips: {chips}
            - Hand: {hand}

            Take into account the community cards and the current bet value to make your decision:
            - Community Cards: {community_cards}
            - Current Bet: {current_bet}

            Review the bet history and opponent behavior to make your decision:
            - Bet History: {bet_history}

            Based on this information, decide your next move. Your options are:
            - Fold: If your hand is weak and opponents show strength.
            - Call: If the bet value is reasonable and your hand has potential.
            - Raise: If your hand is strong and you want to increase the pot size or bluff.
            - Check: If no bet is required and you want to see the next card for free.

            You must have enough chips to call or raise.

            Make a decision now and provide a brief explanation for your choice.

            Format Instructions: {format_instructions}
        """

        prompt = PromptTemplate(template=betting_prompt, input_variables=['chips', 'hand', 'current_bet', 'community_cards', 'bet_history', 'format_instructions'])
        chain = prompt | self.llm | output_parser

        list_str_bet_history = [f"{name} bet {bet} as {role} in stage {stage}" for name, bet, role, stage in game.bet_history]
        str_community_cards = 'Empty' if len(game.community_cards) == 0 else ', '.join([f"{rank} of {suit}" for rank, suit in game.community_cards])
        str_hand = ', '.join([f"{rank} of {suit}" for rank, suit in self.hand])

        bet_decision = chain.invoke(
            {
                "chips": self.chips,
                "hand": str_hand,
                "current_bet": game.current_bet,
                "community_cards": str_community_cards,
                "bet_history": "\n".join(list_str_bet_history),
                "format_instructions": format_instructions,
            }
        )

        print(bet_decision)
        if bet_decision['betting_decision'] == 'Call':
            bet_amount = game.current_bet
        elif bet_decision['betting_decision'] == 'Raise':
            bet_amount = game.current_bet + int(bet_decision['raise_amount'])
        elif bet_decision['betting_decision'] == 'Fold':
            bet_amount = 0
            self.is_active = False
        game.bet_history.append((self.name, bet_amount, bet_decision['betting_decision'], game.stage))
        super().place_bet(bet_amount, game)

        print(f"{self.name} decided to {bet_decision['betting_decision']} with reasoning: {bet_decision['explanation']}. His hand is {self.hand} and community cards are {game.community_cards}.")
        current_bet_history = game.bet_history.copy()
        current_community_cards = game.community_cards.copy()
        game.reasoning_history.append((self.name, bet_decision['explanation'], game.stage, game.current_bet, current_community_cards, current_bet_history))

class Game:
    def __init__(self, players, starting_chips):
        self.deck = create_deck()  # Create and shuffle the deck
        random.shuffle(self.deck)
        self.players = [OpenAIPlayer(name, model, starting_chips) for (name, model) in players]  # Initialize players with AI models
        self.community_cards = []  # List to hold community cards
        self.pot = 0  # Total amount of chips in the pot
        self.current_bet = 0  # Current highest bet
        self.bet_history = []  # History of bets made in the game
        self.reasoning_history = []  # History of players' reasoning for bets
        self.stage = "Pre-flop"  # Current stage of the game
        self.winner = None  # Winner of the game
        self.errors = []  # List to track errors

    def assign_roles(self):
        """Assign roles to players (Dealer, Small Blind, Big Blind) and handle initial bets."""
        for player, role in zip(self.players, PLAYER_ROLES):
            player.role = role
            if role == 'Small Blind':
                player.bet = 1
                player.chips -= 1
                self.pot += 1
                self.bet_history.append((player.name, player.bet, 'Small Blind', self.stage))
            elif role == 'Big Blind':
                player.bet = 2
                player.chips -= 2
                self.pot += 2
                self.bet_history.append((player.name, player.bet, 'Big Blind', self.stage))
            self.current_bet = player.bet

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
        for i, player in enumerate(self.players):
            if not player.is_active:
                continue
            if self.stage == "Pre-flop":
                if player.role == 'Big Blind' or player.role == 'Small Blind':
                    continue
            bet = min(player.chips, self.current_bet)  # Simplified betting logic
            player.place_bet(self)
            self.pot += bet

    def play_round(self):
        """Plays a full round of Texas Hold'em (simplified)."""
        self.assign_roles()
        self.deal_to_players()
        self.take_bets()

        # Flop
        self.stage = "Flop"
        for _ in range(3):
            self.deal_community_card()
        self.take_bets()

        # Turn
        self.stage = "Turn"
        self.deal_community_card()
        self.take_bets()

        # River
        self.stage = "River"
        self.deal_community_card()
        self.take_bets()

        # Showdown
        self.stage = "Showdown"
        self.showdown()

    def showdown(self):
        """Determine the winner (simplified)."""
        player_hands = [(player, best_hand(player.hand, self.community_cards)) for player in self.players if player.is_active]
        if len(player_hands) == 0:
            print("All players have folded. No winner.")
            return
        winner = max(player_hands, key=lambda x: hand_rank(x[1]))[0]
        print(f"The winner is {winner.name} ({winner.model_name}) with hand {winner.hand}")
        for player in self.players:
            print(f"{player.name} has {player.hand} with community cards {self.community_cards}")
        print(f"The pot is {self.pot} chips.")
        self.winner = winner

# Example usage:
player_names = ['Jack', 'Evan', 'Owen']
llm_models = ['gpt-3.5-turbo-1106', 'gpt-4-turbo', 'gpt-4o']
folder_to_save = 'data/complex_evaluation_thorough'
players_with_models = list(zip(player_names, llm_models))
# Get all .pkl files in the specified folder
game_files = glob.glob(f'{folder_to_save}/*.pkl')
game_indices = [int(game_file.split('/')[-1].split('.')[0].split('_')[-1]) for game_file in game_files]
max_index = max(game_indices) if len(game_indices) > 0 else 0

for i in range(max_index, 50):
    random.shuffle(players_with_models)
    game = Game(players_with_models, starting_chips=10)
    game.play_round()
    object_to_save = {"bet_history": game.bet_history, "reasoning_history": game.reasoning_history}
    if len(game.errors) > 0:
        object_to_save["errors"] = game.errors
    if game.winner is not None:
        object_to_save["winner"] = game.winner.name
        object_to_save["role"] = game.winner.role
        object_to_save["winner_model"] = game.winner.model_name
        object_to_save["winning_amount"] = game.pot
    with open(f"{folder_to_save}/game_{i}.pkl", "wb") as f:
        pickle.dump(object_to_save, f)

