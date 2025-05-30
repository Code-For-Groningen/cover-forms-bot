from typing import Any, List, Dict

class BaseNotifier(ABC):
    """
    Base class for all notification handlers.
    """
    
    def __init__(self, **config) -> None:
        self.config = config
    
    @abstractmethod
    def notify(self, attendees: List[Dict[str, Any]], event_form) -> bool:
        """
        Send notifications to the provided attendees.
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the notifier is properly configured.
        """
        pass