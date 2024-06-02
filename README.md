# OpenAI Agents Poker

Welcome to the **OpenAI Agents Poker** project! This experimental project pits different versions of OpenAI's language models—GPT-3.5, GPT-4, and GPT-4o—against each other in games of Texas Hold'em poker. This README will guide you through the setup, execution, and analysis of the poker games.

## Table of Contents
- [OpenAI Agents Poker](#openai-agents-poker)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Analyzing Results](#analyzing-results)

## Introduction

The project simulates Texas Hold'em poker games with AI agents representing different OpenAI models. Each agent makes betting decisions based on their understanding of the game state, including their hand, community cards, bet history, and opponent behavior.

## Installation

To run this project, follow these steps:

1. **Clone the repository:**
    ```sh
    git clone https://github.com/nikogamulin/OpenAI-Agents-Poker.git
    cd OpenAI-Agents-Poker
    ```

2. **Install dependencies:**
    This project requires Python 3.8+ and several Python packages. Install the required packages using pip:
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```sh
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

To start the poker simulation, execute the `poker_agents.py` script:
```sh
python poker_agents.py
```

This script initializes the game, assigns roles to the players, deals cards, and simulates betting rounds until a winner is determined. The game results and players' reasoning are saved in a specified folder.

## Analyzing Results

The project includes Jupyter notebooks for analyzing the results of the games. These notebooks are located in the notebooks directory. Before analyzing your own data, ensure that you have run the games and generated the necessary game logs.



