from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pyshared import ran, List, Opt

app = FastAPI()


class Item(BaseModel):
    id: int
    name: str
    type: str
    desc: str


class ItemList(BaseModel):
    items: List[Item]


class ItemFamily(BaseModel):
    lead: Item
    fam: List[Item]


types = ["Item", "ItemList", "ItemFamily"]
names = ["Nm{}".format(i) for i in range(100)]
descriptions = ["Dsc{}".format(i) for i in range(100)]


def create_items():
    base_items = [
        Item(
            id=i,
            name=ran.choice(names),
            type="Item",
            desc=ran.choice(descriptions),
        )
        for i in range(90)
    ]
    list_items = [
        ItemList(items=ran.sample(base_items, ran.randint(2, 5)))
        for _ in range(5)
    ]
    family_items = [
        ItemFamily(
            lead=ran.choice(base_items),
            fam=ran.sample(base_items, ran.randint(2, 5)),
        )
        for _ in range(5)
    ]

    return base_items + list_items + family_items


items = create_items()


@app.get("/items/", response_model=List[Item])
async def read_items(type: Opt[str] = None):
    if type:
        return [item for item in items if item.type == type]
    return items


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    item = next((item for item in items if item.id == item_id), None)
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.get('/openapi.json')
async def openapi():
    return app.openapi()


client = TestClient(app)

print(client.get('/openapi.json').json())
