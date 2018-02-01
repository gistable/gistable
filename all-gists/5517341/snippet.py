products = Product.select().where(
    Product.id << [161,162,163,164,165]).where(
        ~(Product.brand_name >> None)
    )