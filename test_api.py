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


class Data:
    people: List[Person] = []
    houses: List[House] = []
    homeless: List[Person] = []
    housed: List[Person] = []

    def __init__(self):
        for i in range(100):
            self.people.append(
                Person(id=i, name=f'Person {i}', age=ran.randint(1, 100))
            )
        pool = self.people.copy()
        for i in range(10):
            occupants = [
                pool.pop(ran.randint(0, len(pool) - 1))
                for _ in range(ran.randint(1, 7))
            ]
            self.houses.append(
                House(
                    id=i,
                    address=f'Address {i}',
                    owner=pool.pop(ran.randint(0, len(pool) - 1)),
                    occupants=occupants,
                )
            )
        self.homeless = pool
        self.housed = [p for h in self.houses for p in h.occupants]

    def __repr__(self):
        return "Data(people={}, houses={}, homeless={}, housed={})".format(
            len(self.people),
            len(self.houses),
            len(self.homeless),
            len(self.housed),
        )


data = Data()


@app.get("/openapi.json")
async def openapi():
    return app.openapi()


@app.get("/people")
async def get_people():
    return data.people


client = TestClient(app)

print(str(client.get("/people").json())[0:100], data, sep="\n")
