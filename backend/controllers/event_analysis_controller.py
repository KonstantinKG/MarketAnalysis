from logging import Logger


class EventAnalysisController:
    def __init__(self, config: dict, logger: Logger):
        self._config=config
        self._logger=logger
