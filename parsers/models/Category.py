class Category:
    def __init__(
            self,
            id: str,
            parent_id: str or None,
            code: str,
            name: str
    ):
        self.id = id
        self.parent_id = parent_id
        self.code = code
        self.name = name
