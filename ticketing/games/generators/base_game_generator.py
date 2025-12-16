from abc import ABC, abstractmethod
from typing import List, Tuple, Any


class BaseGameGenerator(ABC):
    def __init__(self, game_info, addl_imgs_tracker):
        """
        Args:
            game_info: Global game settings.
            addl_imgs_tracker: The 'gi.AddImages' object used to TRACK
                               available images. It is NOT a static list.
        """
        self.game_info = game_info
        self.addl_imgs_tracker = addl_imgs_tracker

        # State tracking
        self.nw_pool: List[str] = []
        self.is_first: bool = False
        self.batches: List[List[Any]] = []

    def initialize_batches(self):
        perms = getattr(self.game_info, 'permutations', 1)
        self.batches = [[] for _ in range(perms)]

    @abstractmethod
    def generate(self) -> Tuple[List[List[Any]], List[str]]:
        pass

    def set_start_state(self, existing_pool: List[str], is_first: bool):
        self.nw_pool = existing_pool
        self.is_first = is_first
