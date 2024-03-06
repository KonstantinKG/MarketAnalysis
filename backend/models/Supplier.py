class Supplier:
    TABLE = 'suppliers'
    COLUMNS = ["id", "product_id", "name", "price", "rating"]
    ON_CONFLICT = f"ON CONFLICT (product_id, name) DO UPDATE SET {', '.join(f'{c} = EXCLUDED.{c}' for c in COLUMNS)}"

    def __init__(self, id: int or None, product_id: int, name: str, price: float, rating: float):
        self.id = id
        self.product_id = product_id
        self.name = name
        self.price = price
        self.rating = rating
