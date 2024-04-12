#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pyshared import ran, List, Opt, RanData

app = FastAPI()

rd = RanData()


class Prop(BaseModel):
    pstr: str = rd.str
    pbool: bool = rd.bool
    pint: int = rd.int
    pfloat: float = rd.float


class Item(BaseModel):
    id: int
    parent: Opt["Item"] = None
    children: List["Item"] = []
    props: List[Prop] = [Prop() for _ in range(0, 2)]


def gen_items(n=10) -> List[Item]:
    pool = [x for x in range(1, n)]
    parents = [pool.pop() for _ in range(n // 5)]
    parents = [Item(id=x) for x in parents]
    items = parents.copy()
    while pool:
        parent = ran.choice(parents)
        child = pool.pop()
        items.append(Item(id=child, parent=parent))
    return items


items = gen_items()


class Group(BaseModel):
    id: int
    items: List[Item] = []
    props: List[Prop] = [Prop() for _ in range(0, 2)]


groups = [Group(id=i, items=items) for i in [1, 2]]

for i in items:
    groups[0 if i.id % 2 == 0 else 1].items.append(i)


@app.get("/openapi.json")
async def openapi():
    return app.openapi()


@app.get("/items", response_model=List[Item])
async def get_items():
    return items


@app.get("/groups", response_model=List[Group])
async def get_groups():
    return groups


client = TestClient(app)

# print(str(client.get("/openapi.json").json())[0:1000])
print(str(client.get("/items").json())[0:1000])
