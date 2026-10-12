from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field as PydanticField


class LoginRequest(BaseModel):
    login: str = PydanticField(min_length=1, max_length=100)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    last_name: str
    first_name: str
    middle_name: str | None
    login: str
    role: str


class CategoryCreate(BaseModel):
    name: str = PydanticField(min_length=1, max_length=100)


class CategoryUpdate(BaseModel):
    name: str = PydanticField(min_length=1, max_length=100)


class CategoryRead(BaseModel):
    category_id: int
    name: str


class SubcategoryCreate(BaseModel):
    name: str = PydanticField(min_length=1, max_length=100)
    category_id: int = PydanticField(gt=0)


class SubcategoryUpdate(BaseModel):
    name: str | None = PydanticField(default=None, min_length=1, max_length=100)
    category_id: int | None = PydanticField(default=None, gt=0)


class SubcategoryRead(BaseModel):
    subcategory_id: int
    name: str
    category_id: int


class SizeAvailability(BaseModel):
    size_id: int
    size_value: str
    quantity_available: int


class ProductFields(BaseModel):
    category_id: int = PydanticField(gt=0)
    subcategory_id: int | None = PydanticField(default=None, gt=0)
    image_path: str | None = PydanticField(default=None, max_length=500)
    product_name: str = PydanticField(min_length=1, max_length=200)
    manufacturer: str = PydanticField(min_length=1, max_length=150)
    description: str | None = PydanticField(default=None, max_length=2000)
    composition: str | None = PydanticField(default=None, max_length=1000)
    price: Decimal = PydanticField(gt=0, max_digits=10, decimal_places=2)


class ProductCreate(ProductFields):
    pass


class ProductUpdate(BaseModel):
    category_id: int | None = PydanticField(default=None, gt=0)
    subcategory_id: int | None = PydanticField(default=None, gt=0)
    image_path: str | None = PydanticField(default=None, max_length=500)
    product_name: str | None = PydanticField(default=None, min_length=1, max_length=200)
    manufacturer: str | None = PydanticField(default=None, min_length=1, max_length=150)
    description: str | None = PydanticField(default=None, max_length=2000)
    composition: str | None = PydanticField(default=None, max_length=1000)
    price: Decimal | None = PydanticField(
        default=None, gt=0, max_digits=10, decimal_places=2
    )


class StockUpdate(BaseModel):
    quantity_available: int = PydanticField(ge=0, le=1_000_000)


class StockBySizeValue(BaseModel):
    size_value: str = PydanticField(min_length=1, max_length=50)
    quantity_available: int = PydanticField(ge=0, le=1_000_000)


class ProductRead(BaseModel):
    product_id: int
    category_id: int
    category: str
    subcategory_id: int | None
    subcategory: str | None
    image_path: str | None
    product_name: str
    manufacturer: str
    description: str | None
    composition: str | None
    price: Decimal
    discounted_price: Decimal
    discount_percent: int
    total_quantity: int
    low_stock: bool


class ProductDetail(ProductRead):
    sizes: list[SizeAvailability]
    size_range: list[str]


class OrderItemCreate(BaseModel):
    product_id: int = PydanticField(gt=0)
    size_id: int = PydanticField(gt=0)
    quantity: int = PydanticField(gt=0, le=10000)


class OrderCreate(BaseModel):
    user_id: int | None = PydanticField(default=None, gt=0)
    items: list[OrderItemCreate] = PydanticField(min_length=1)


class OrderItemRead(BaseModel):
    order_item_id: int
    product_id: int
    product_name: str
    manufacturer: str
    size_id: int
    size_value: str
    quantity: int
    price: Decimal
    line_total: Decimal


class OrderRead(BaseModel):
    order_id: int
    order_date: datetime
    user_id: int
    customer_full_name: str
    total: Decimal
    items: list[OrderItemRead]


class OrderSummary(BaseModel):
    order_id: int
    order_date: datetime
    user_id: int
    customer_full_name: str
    total: Decimal


class OrderDateUpdate(BaseModel):
    order_date: datetime
