from .base import BasePlatform

from cover.event import Event
class Wapp(BasePlatform):
    def __init__(self, source: str, form_url:str, target: str, event:Event) -> None:
        super().__init__(source, form_url, target, event)
        self.source = source
        self.target = target
        self.kwargs = kwargs

    def _BasePlatform__send_message(self, image: Image) -> bool:
        ...