from .base import BasePlatform

class Wapp(BasePlatform):
    def __init__(self, source: str, target: str, **kwargs):
        super().__init__(source, target, **kwargs)
        self.source = source
        self.target = target
        self.kwargs = kwargs

    def send_message(self) -> bool:
        ...