export type Role = 'user' | 'manager' | 'admin' | string
export type User = {
  user_id: number; last_name: string; first_name: string; middle_name: string | null; login: string; role: Role
}
export type Category = { category_id: number; name: string }
export type Subcategory = { subcategory_id: number; name: string; category_id: number }
export type SizeAvailability = { size_id: number; size_value: string; quantity_available: number }
export type Product = {
  product_id: number; category_id: number; category: string; subcategory_id: number | null; subcategory: string | null
  image_path: string | null; product_name: string; manufacturer: string; description: string | null; composition: string | null
  price: number; discounted_price: number; discount_percent: number; total_quantity: number; low_stock: boolean
}
export type ProductDetail = Product & { sizes: SizeAvailability[]; size_range: string[] }
export type CartLine = { product: Product; size_id: number; size_value: string; quantity: number }
export type OrderSummary = { order_id: number; order_date: string; user_id: number; customer_full_name: string; total: number }
export type OrderItem = { order_item_id: number; product_id: number; product_name: string; manufacturer: string; size_id: number; size_value: string; quantity: number; price: number; line_total: number }
export type OrderDetail = OrderSummary & { items: OrderItem[] }
export type Page = 'login' | 'main' | 'orders'
export type ProductForm = {
  category_id: string; subcategory_id: string; product_name: string; manufacturer: string
  description: string; composition: string; price: string
}
