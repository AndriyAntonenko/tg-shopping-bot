from dataclasses import dataclass
from sqlite3 import Connection

@dataclass
class GetProductsListParams:
  limit: int = 10
  cursor: int = 0
  sort_desc: bool = False

@dataclass
class ProductItem:
  id: int
  name: str
  description: str
  price: float
  currency: str
  created_at: str

def from_db_row_to_product_item(row) -> ProductItem:
  return ProductItem(
    id=row[0],
    name=row[1],
    description=row[2],
    price=row[3],
    currency=row[4],
    created_at=row[5]
  )

class ProductService:
  db_connection: Connection
  
  def __init__(self, db_connection: Connection):
    self.db_connection = db_connection
  
  # Accept arguments like limit, cursor for pagination and sort direction
  def get_products_list(self, params: GetProductsListParams):
    cursor_obj = self.db_connection.cursor()
    order = "DESC" if params.sort_desc else "ASC"
    condition = '''(o.id IS NULL OR o.status = 'cancelled') AND p.id <= ?''' if params.cursor > 0 else "(o.id IS NULL OR o.status = 'cancelled')"
    query = f'''
      SELECT p.* FROM products p
      LEFT JOIN orders o ON p.id = o.product_id
      WHERE {condition}
      ORDER BY p.id {order}
      LIMIT ?;
    '''
    args = (params.cursor, params.limit + 1) if params.cursor > 0 else (params.limit + 1,)
    cursor_obj.execute(query, args) # Fetch one extra to check for more pages
    products_raws = cursor_obj.fetchall()
    products = map(from_db_row_to_product_item, products_raws[:params.limit])  # Return only the requested limit
    fetch_next_cursor = None
    if len(products_raws) > params.limit:
      fetch_next_cursor = products_raws[params.limit][0]  # id of the last item in the current page

    return list(products), fetch_next_cursor
