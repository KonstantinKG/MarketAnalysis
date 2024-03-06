import datetime


class Product:
    TABLE = 'products'
    COLUMNS = ["id", "src_id", "category_id", "name", "image", "rating", "description", "characteristics", "relevance"]
    ON_CONFLICT = f"ON CONFLICT (id) DO UPDATE SET {', '.join(f'{c} = EXCLUDED.{c}' for c in COLUMNS)}"

    def __init__(self, id: str or None, src_id: str, category_id: str, name: str, image: str, rating: float, description: str,
                 characteristics: str):
        self.id = id
        self.src_id = src_id
        self.category_id = category_id
        self.name = name
        self.image = image
        self.rating = rating
        self.description = description
        self.characteristics = characteristics
        self.relevance = datetime.datetime.now()
