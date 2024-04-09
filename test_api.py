#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pyshared import ran, List, Opt

app = FastAPI()


class IDBase(BaseModel):
    id: int


class Person(IDBase):
    name: str
    age: int


class Building(IDBase):
    address: str
    owner: Person


class House(Building):
    occupants: List[Person]


unique_ids = [x for x in range(1, 1000)]


data = {
    "people": {x: Person(id=x, name=ran(), age=ran()) for x in unique_ids},
    "buildings": {
        x: Building(id=x, address=ran(), owner=data["people"][ran()])
        for x in unique_ids
    },
    "houses": {
        x: House(
            id=x,
            address=ran(),
            owner=data["people"][ran()],
            occupants=[data["people"][ran()] for _ in range(1, 5)],
        )
        for x in unique_ids
    },
}


@app.get("/openapi.json")
async def openapi():
    return app.openapi()


@app.get("/people")
async def people():
    return data["people"]


client = TestClient(app)

print(client.get("/people").json(), data, sep="\n")
