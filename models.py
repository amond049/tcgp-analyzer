from enum import Enum
import datetime

# MODELS 

# This variable will keep track of all of the expansions that have been released for the TCGP, will need to be updated when a new set releases 
expansions = {
    'P-A': 'Promo-A',
    'A1': 'Genetic Apex',
    'A1a': 'Mythical Island',
    'A2': 'Space-Time Smackdown',
    'A2a': 'Triumphant Light',
    'A2b': 'Shining Revelry',
    'A3': 'Celestial Guardians',
    'A3a': 'Extradimensional Crisis',
    'A3b': 'Eevee Grove',
    'A4': 'Wisdom of Sea and Sky',
    'A4a': 'Secluded Springs',
    'A4b': 'Deluxe Pack: ex',
    'P-B': 'Promo-B',
    'B1': 'Mega Rising',
    'B1a': 'Crimson Blaze'
}

'''
Enum representing the different types that a Pokemon can be
'''
class PokemonType(Enum):
    GRASS = 1
    FIRE = 2
    WATER = 3
    LIGHTNING = 4
    PSYCHIC = 5
    FIGHTING = 6
    DARKNESS = 7
    METAL = 8
    COLORLESS = 9
    DRAGON = 10
    NONE = 11

'''
Class representing the structure of an expansion record the game has had
'''
class Expansion:
    def __init__(self, name: str, release_date: datetime, number_cards: int, expansion_identifier: str):
        self._name = name 
        self._release_date = release_date 
        self._number_cards = number_cards
        # This will be one of the keys specified in the expansions dictionary
        self._expansion_identifier = expansion_identifier
    
    '''
    Getters
    '''
    def get_name(self) -> str: 
        return self._name 
    
    def get_release_date(self) -> datetime: 
        return self._release_date

    def get_number_cards(self) -> int:
        return self._number_cards

    def get_expansion_identifier(self) -> str:
        return self._expansion_identifier

'''
Class representing the structure of an attack that a Pokemon could have
'''
class PokemonMove:
    def __init__(self, name: str, damage: str, description = ''):
        self._name = name
        self._damage = damage
        self._description = description

    '''
    Getters
    '''
    def get_name(self) -> str:
        return self._name

    def get_damage(self) -> str:
        return self._damage

    def get_description(self) -> str:
        return self._description
    
    '''
    Setters
    '''
    def set_name(self, name: str):
        self._name = name
    
    def set_damage(self, damage: str):
        self._damage = damage

    def set_description(self, description: str):
        self._description = description

'''
Class representing the structure of an ability that a Pokemon might have 
'''
class PokemonAbility: 
    def __init__(self, name: str, description = ''):
        self._name = name
        self._description = description
    
    '''
    Getters
    '''
    def get_name(self) -> str:
        return self._name
    
    def get_description(self) -> str:
        return self._description
    
    '''
    Setters
    '''
    def set_name(self, name: str):
        self._name = name
    
    def set_description(self, description: str):
        self._description = description

class Card:
    def __init__(self, name: str, rarity: int, card_image: str, is_promo: bool, illustrator: str, expansion: Expansion, expansion_number: int):
        self._name = name
        self._rarity = rarity
        self._card_image = card_image
        self._is_promo = is_promo
        self._illustrator = illustrator
        self._expansion = expansion
        self._expansion_number = expansion_number
    
    '''
    Getters
    '''
    def get_name(self) -> str:
        return self._name

    def get_rarity(self) -> int:
        return self._rarity

    def get_card_image(self) -> str:
        return self._card_image

    def get_is_promo(self) -> bool:
        return self._is_promo

    def get_illustrator(self) -> str:
        return self._illustrator

    def get_expansion(self) -> str:
        return self._expansion

    def get_expansion_number(self) -> int:
        return self._expansion_number

    '''
    Setters
    '''
    def set_name(self, name: str):
        self._name = name
    
    def set_rarity(self, rarity: int):
        self._rarity = rarity

    def set_card_image(self, card_image: str):
        self._card_image = card_image

    def set_is_promo(self, is_promo: bool):
        self._is_promo = is_promo
    
    def set_illustrator(self, illustrator: str):
        self._illustrator = illustrator

class PokemonCard(Card):
    def __init__(self, name: str, health: int, type: PokemonType, weakness: PokemonType, retreat_cost: int, rarity: int, moves: list[PokemonMove], ability: PokemonAbility, card_image: str, is_promo: bool, illustrator: str, expansion: str, expansion_number: int):
        super().__init__(name, rarity, card_image, is_promo, illustrator, expansion, expansion_number)
        self._health = health
        self._type = type
        self._weakness = weakness 
        self._retreat_cost = retreat_cost
        self._moves = moves
        self._ability = ability 
    
    '''
    Getters
    '''
    def get_health(self) -> int:
        return self._health

    def get_type(self) -> PokemonType:
        return self._type

    def get_stage(self) -> int:
        return self._stage

    def get_weakness(self) -> PokemonType:
        return self._weakness

    def get_retreat_cost(self) -> int:
        return self._retreat_cost

    def get_moves(self) -> list[PokemonMove]:
        return self._moves

    def get_ability(self) -> PokemonAbility:
        return self._ability

    '''
    Setters
    '''
    def set_health(self, health: int):
        self._health = health

    def set_type(self, type: PokemonType):
        self._type = type

    def set_stage(self, stage: int):
        self._stage = stage

    def set_weakness(self, weakness: PokemonType):
        self._weakness = weakness

    def set_retreat_cost(self, retreat_cost: int):
        self._retreat_cost = retreat_cost

    def set_moves(self, moves: list[PokemonMove]):
        self._moves = moves

    def set_ability(self, ability: PokemonAbility):
        self._ability = ability

class StageBasicPokemonCard(PokemonCard):
    def __init__(self, name: str, health: int, type: PokemonType, weakness: PokemonType, retreat_cost: int, rarity: int, moves: list[PokemonMove], ability: PokemonAbility, card_image: str, is_promo: bool, illustrated_by: str, expansion: Expansion, expansion_number: int):
        super().__init__(name, health, type, weakness, retreat_cost, rarity, moves, ability, card_image, is_promo, illustrated_by, expansion, expansion_number)
        # Basic Pokemon will have a stage of 0, this is since the second stage pokemon is technically a stage 1 Pokemon
        self._stage = 0
    
    '''
    Getters
    '''
    def get_stage(self) -> int: 
        return self._stage
    
class StageNonBasicPokemonCard(PokemonCard):
    def __init__(self, name: str, health: int, type: PokemonType, weakness: PokemonType, retreat_cost: int, rarity: int, moves: list[PokemonMove], ability: PokemonAbility, card_image: str, is_promo: bool, illustrated_by: str, stage: int, evolves_from: str, expansion: Expansion, expansion_number: int):
        super().__init__(name, health, type, weakness, retreat_cost, rarity, moves, ability, card_image, is_promo, illustrated_by, expansion, expansion_number)
        self._stage = stage
        self._evolves_from = evolves_from
    
    '''
    Getters
    '''
    def get_stage(self) -> int:
        return self._stage

    def get_evolves_from(self) -> str:
        return self._evolves_from

class TrainerItemCard(Card):
    # -1 is the flag value for an item that is NOT a fossil
    def __init__(self, name: str, rarity: int, card_image: str, is_promo: bool, illustrated_by: str, description: str, expansion: Expansion, expansion_number: int, health = -1):
        super().__init__(name, rarity, card_image, is_promo, illustrated_by, expansion, expansion_number)
        self._health = health
        self._description = description 
    
    '''
    Getters
    '''
    def get_health(self) -> int:
        # Only fossils, which are treated as an Item will have a health, so this check ensures that we only try and return the health for a fossil, since it will have a non-zero health value
        if self._health > 0:
            return self._health
    
    def get_description(self) -> str:
        return self._description


class TrainerSupporterOrToolCard(Card):
    # Since the class definition for supporter and tool type cards are the exact same, I will be using one class to represent them and a boolean value will differentiate them
    # A getter for is_supporter is not required since there is no situation I foresee needing to retrieve this information, but this is subject to change as develoment continues
    def __init__(self, name: str, rarity: int, card_image: str, is_promo: bool, illustrated_by: str, description: str, is_supporter: bool, expansion: Expansion, expansion_number: int):
        super().__init__(name, rarity, card_image, is_promo, illustrated_by, expansion, expansion_number)
        self._description = description
        self._is_supporter = is_supporter

    '''
    Getters
    '''
    def get_description(self) -> str:
        return self._description
    
    def get_is_supporter(self) -> str:
        return self._is_supporter
