class Product:
    def __init__(self, id: int, name: str, image: str, price: int, rating: int, description: str, characteristics: str):
        self.id = id
        self.name = name
        self.image = image
        self.price = price
        self.rating = rating if 0 <= rating <= 10 else None
        self.description = description
        self.characteristics = characteristics
