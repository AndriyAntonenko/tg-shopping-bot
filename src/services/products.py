from dataclasses import dataclass
from ..db.connection import get_db_connection
from .orders import OrderStatus

@dataclass
class GetProductsListParams:
  limit: int = 10
  cursor: int = 0
  sort_desc: bool = False

@dataclass
class ProductItem:
  id: int
  name: str
  image_url: str | None
  description: str
  price: float
  currency: str
  created_at: str

def from_db_row_to_product_item(row) -> ProductItem:
  return ProductItem(
    id=row[0],
    name=row[1],
    description=row[2],
    image_url=row[3],
    price=row[4],
    currency=row[5],
    created_at=row[6]
  )

class ProductService:
  async def get_products_count(self) -> int:
    conn = await get_db_connection()
    cursor_obj = await conn.cursor()
    query = '''
      SELECT
        COUNT(*)
      FROM products p
      LEFT JOIN orders o ON o.product_id = p.id
      WHERE o.id IS NULL OR o.status = ?;
    '''
    await cursor_obj.execute(query, (OrderStatus.CANCELED.value,))
    count = (await cursor_obj.fetchone())[0]
    return count
  
  # Accept arguments like limit, cursor for pagination and sort direction
  async def get_products_list(self, params: GetProductsListParams):
    conn = await get_db_connection()
    cursor_obj = await conn.cursor()
    order = "DESC" if params.sort_desc else "ASC"
    condition = '''p.id <= ? AND (o.id IS NULL OR o.status = ?)''' if params.cursor > 0 else "(o.id IS NULL OR o.status = ?)"
    query = f'''
      SELECT p.* FROM products p
      LEFT JOIN orders o ON p.id = o.product_id
      WHERE {condition}
      ORDER BY p.id {order}
      LIMIT ?;
    '''
    args = (params.cursor, OrderStatus.CANCELED.value, params.limit + 1) if params.cursor > 0 else (OrderStatus.CANCELED.value, params.limit + 1,)
    await cursor_obj.execute(query, args) # Fetch one extra to check for more pages
    products_raws = await cursor_obj.fetchall()
    products = map(from_db_row_to_product_item, products_raws[:params.limit])  # Return only the requested limit
    fetch_next_cursor = None
    if len(products_raws) > params.limit:
      fetch_next_cursor = products_raws[params.limit][0]  # id of the last item in the current page

    return list(products), fetch_next_cursor

  async def get_product_by_id(self, product_id: int) -> ProductItem | None:
    conn = await get_db_connection()
    cursor_obj = await conn.cursor()
    query = '''
      SELECT p.* FROM products p
      LEFT JOIN orders o ON p.id = o.product_id
      WHERE p.id = ? AND (o.id IS NULL OR o.status = 'canceled')
    '''
    await cursor_obj.execute(query, (product_id,))
    row = await cursor_obj.fetchone()
    if row is None:
      return None
    return from_db_row_to_product_item(row)

  async def add_product(
    self,
    name: str,
    description: str,
    image_url: str,
    price: float,
    currency: str
  ):
    conn = await get_db_connection()
    cursor_obj = await conn.cursor()
    query = '''
      INSERT INTO products (name, description, image_url, price, currency)
      VALUES (?, ?, ?, ?, ?);
    '''
    await cursor_obj.execute(query, (name, description, image_url, price, currency))
    await conn.commit()
    return cursor_obj.lastrowid
