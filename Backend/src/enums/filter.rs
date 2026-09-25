pub enum Filter {
    TextSearch(String), // Ищет по Name / Description
    SalerName(String),  // Ищет по имени продавца
    MinPrice(f64),      // PriceMore
    MaxPrice(f64),      // PriceLess
    MinReviews(i32),    // Миниамльное количество отзывов
}
