"""Merge duplicate categories/subcategories and preserve product foreign keys.

Run once from the backend root after taking a PostgreSQL backup:
    python -m scripts.dedupe_categories
"""

from __future__ import annotations

from sqlmodel import Session, select

from db.database import engine
from model import Category, Product, Subcategory


def normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


def run() -> tuple[int, int]:
    merged_categories = 0
    merged_subcategories = 0
    with Session(engine) as session:
        try:
            categories = list(
                session.exec(select(Category).order_by(Category.category_id)).all()
            )
            canonical_categories: dict[str, Category] = {}
            for category in categories:
                key = normalize(category.name)
                canonical = canonical_categories.get(key)
                if canonical is None:
                    category.name = " ".join(category.name.split())
                    canonical_categories[key] = category
                    continue

                subcategories = list(
                    session.exec(
                        select(Subcategory).where(
                            Subcategory.category_id == category.category_id
                        )
                    ).all()
                )
                for subcategory in subcategories:
                    sub_key = normalize(subcategory.name)
                    target = next(
                        (
                            item
                            for item in session.exec(
                                select(Subcategory).where(
                                    Subcategory.category_id == canonical.category_id
                                )
                            ).all()
                            if normalize(item.name) == sub_key
                        ),
                        None,
                    )
                    if target is None:
                        subcategory.category_id = canonical.category_id
                        subcategory.name = " ".join(subcategory.name.split())
                    else:
                        for product in session.exec(
                            select(Product).where(
                                Product.subcategory_id == subcategory.subcategory_id
                            )
                        ).all():
                            product.subcategory_id = target.subcategory_id
                        session.delete(subcategory)
                        merged_subcategories += 1
                for product in session.exec(
                    select(Product).where(Product.category_id == category.category_id)
                ).all():
                    product.category_id = canonical.category_id
                session.delete(category)
                merged_categories += 1
                session.flush()

            session.flush()
            all_categories = list(session.exec(select(Category)).all())
            for category in all_categories:
                subcategories = list(
                    session.exec(
                        select(Subcategory)
                        .where(Subcategory.category_id == category.category_id)
                        .order_by(Subcategory.subcategory_id)
                    ).all()
                )
                canonical_subcategories: dict[str, Subcategory] = {}
                for subcategory in subcategories:
                    key = normalize(subcategory.name)
                    target = canonical_subcategories.get(key)
                    if target is None:
                        subcategory.name = " ".join(subcategory.name.split())
                        canonical_subcategories[key] = subcategory
                        continue
                    for product in session.exec(
                        select(Product).where(
                            Product.subcategory_id == subcategory.subcategory_id
                        )
                    ).all():
                        product.subcategory_id = target.subcategory_id
                    session.delete(subcategory)
                    merged_subcategories += 1
                session.flush()

            session.commit()
        except Exception:
            session.rollback()
            raise
    return merged_categories, merged_subcategories


if __name__ == "__main__":
    categories, subcategories = run()
    print(f"Готово. Объединено категорий: {categories}; подкатегорий: {subcategories}.")
