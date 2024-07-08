from asyncio import gather

from db import db
from models.cat_model import NextRoundCatModel, CurrentRoundCatCreate

next_round_cat_ref = db.collection("NextRoundCats")
current_round_cat_ref = db.collection("CurrentRoundCats")


async def select_all_next_round_cats() -> list[NextRoundCatModel]:
    docs = [doc async for doc in next_round_cat_ref.stream()]
    next_round_cats = [NextRoundCatModel(**doc.to_dict(), **{"id": doc.id}) for doc in docs]
    return next_round_cats


async def delete_all_next_round_cats(cats: list[NextRoundCatModel]) -> None:
    delete_tasks = [next_round_cat_ref.document(cat.id).delete() for cat in cats]
    await gather(*delete_tasks)


async def insert_current_round_cats(cats: list[CurrentRoundCatCreate]) -> None:
    cats_dicts = [cat.model_dump() for cat in cats]
    new_cats_refs = [current_round_cat_ref.document() for _ in range(len(cats_dicts))]
    insert_operations = [new_cat_ref.set(cat_dict) for cat_dict, new_cat_ref in zip(cats_dicts, new_cats_refs)]
    await gather(*insert_operations)
