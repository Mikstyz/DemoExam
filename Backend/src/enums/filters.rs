pub enum Filter {
    TextSearch(String), // Ищет по Name / Description
    SalerName(String),  // Ищет по имени продавца
    MinPrice(f64),      // PriceMore
    MaxPrice(f64),      // PriceLess
    MinReviews(i32),    // Миниамльное количество отзывов
}

pub enum SortBy {
    Popularity, // Популярность товара
    DateAdded,  // Дата добавления
    PriceAsc,   // Сначала дешевые
    PriceDesc,  // Сначала дорогие
}
