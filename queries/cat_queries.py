from asyncio import gather

from db import db
from models.cat_model import (
    NextRoundCatModel,
    CurrentRoundCatCreate,
    CurrentRoundCatModel,
    CatOfTheWeekCreate,
)

next_round_cat_ref = db.collection("NextRoundCats")
current_round_cat_ref = db.collection("CurrentRoundCats")
cat_of_the_week_ref = db.collection("CatsOfTheWeeks")


class CatQueries:
    @staticmethod
    async def select_all_next_round_cats() -> list[NextRoundCatModel]:
        docs = [doc async for doc in next_round_cat_ref.stream()]
        next_round_cats = [
            NextRoundCatModel(**doc.to_dict(), **{"id": doc.id}) for doc in docs
        ]
        return next_round_cats

    @staticmethod
    async def delete_all_next_round_cats(cats: list[NextRoundCatModel]) -> None:
        delete_tasks = [next_round_cat_ref.document(cat.id).delete() for cat in cats]
        await gather(*delete_tasks)

    @staticmethod
    async def delete_all_current_round_cats() -> None:
        cats_ids = [doc.id async for doc in current_round_cat_ref.stream()]
        delete_tasks = [
            current_round_cat_ref.document(cat_id).delete() for cat_id in cats_ids
        ]
        await gather(*delete_tasks)

    @staticmethod
    async def insert_current_round_cats(cats: list[CurrentRoundCatCreate]) -> None:
        cats_dicts = [cat.model_dump() for cat in cats]
        new_cats_refs = [
            current_round_cat_ref.document() for _ in range(len(cats_dicts))
        ]
        insert_operations = [
            new_cat_ref.set(cat_dict)
            for cat_dict, new_cat_ref in zip(cats_dicts, new_cats_refs)
        ]
        await gather(*insert_operations)

    @staticmethod
    async def select_winning_cat() -> CurrentRoundCatModel:
        all_cats_docs = [doc async for doc in current_round_cat_ref.stream()]
        all_cats = [
            CurrentRoundCatModel(id=cat_doc.id, **cat_doc.to_dict())
            for cat_doc in all_cats_docs
        ]
        cat_with_highest_score = max(all_cats, key=lambda cat: cat.likes - cat.dislikes)

        return cat_with_highest_score

    @staticmethod
    async def insert_cat_of_the_week(cat_of_the_week: CatOfTheWeekCreate) -> None:
        cat_of_the_week_dict = cat_of_the_week.model_dump()
        new_cotw_ref = cat_of_the_week_ref.document()
        await new_cotw_ref.set(cat_of_the_week_dict)
