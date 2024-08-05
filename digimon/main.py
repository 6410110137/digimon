from fastapi import FastAPI, HTTPException

from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None
    price: float = 0.12
    tax: float | None = None


class CreatedItem(BaseItem):
    pass

class UpdatedItem(BaseItem):
    pass

class Item(BaseItem):
    id: int


class DBItem(Item, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_size: int
    size_per_page: int


connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:241241@localhost/digimondb",
    echo=True,
    connect_args=connect_args,
)


SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/items")
async def create_item(item: CreatedItem) -> Item:
    print("created_item", item)
    data = item.model_dump()
    dbitem = DBItem(**data)
    with Session(engine) as session:
        session.add(dbitem)
        session.commit()
        session.refresh(dbitem)

    # return Item.parse_obj(dbitem.dict())
    return Item.model_validate(dbitem)


@app.get("/items")
async def read_items() -> ItemList:
    with Session(engine) as session:
        items = session.exec(select(DBItem)).all()

    return ItemList.model_validate(dict(items=items, page_size=0, page=0, size_per_page=0))


@app.get("/items/{item_id}")
async def read_item(item_id: int) -> Item:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item:
            return Item.model_validate(db_item)
    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: UpdatedItem) -> Item:
    print("update_item", item)
    data = item.dict()
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in data.items():
            setattr(db_item, key, value)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)

    return Item.model_validate(db_item)


@app.delete("/items/{item_id}")
async def delete_item(item_id: int) -> dict:
    with Session(engine) as session:
        db_item = session.get(DBItem, item_id)
        session.delete(db_item)
        session.commit()

    return dict(message="delete success")