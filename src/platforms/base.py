from abc import ABC, abstractmethod
from typing import Any

class BasePlatform(ABC):
    """
    Base class for all platforms.
    """

    def __init__(self, source: str, target: str, **kwargs: Any):
        self.source = source
        self.target = target
        self.kwargs = kwargs
    
    @abstractmethod
    def send_message(self) -> bool:
        """
        Send a message to the target platform.
        """
        pass
