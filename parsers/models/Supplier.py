class Supplier:
    def __init__(self, id: int, product_id: int, name: str, price: int, rating: int):
        self.id = id
        self.product_id = product_id
        self.name = name
        self.price = price
        self.rating = rating if 0 <= rating <= 10 else None
