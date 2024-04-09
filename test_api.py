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


class City(IDBase):
    name: str
    buildings: List[Building]
    governor: Person


class Region(IDBase):
    name: str
    cities: List[City]


class Country(IDBase):
    name: str
    regions: List[Region]
    president: Person
    capital: City


unique_ids = [x for x in range(1, 10000000)]


class Data:
    FIRST_NAMES = ["Alice", "Bob", "Charlie", "David", "Eva"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Jones", "Brown"]
    STREET_NAMES = ["Elm", "Oak", "Pine", "Maple", "Birch"]
    STREET_TYPES = ["St", "Rd", "Ave", "Blvd", "Ln"]
    CITY_PARTS = ["Spring", "Shell", "Ogden", "River", "Clear"]
    CITY_SUFFIXES = ["field", "ville", "town", "berg", "burgh"]
    people: list[Person]
    buildings: list[Building]
    cities: list[City]
    regions: list[Region]
    countries: list[Country]
    cats = (
        (Person, "person", "people"),
        (Building, "building", "buildings"),
        (City, "city", "cities"),
        (Region, "region", "regions"),
        (Country, "country", "countries"),
    )

    def __init__(self):
        self.people = [
            Person(
                name=f"{ran.choice(self.FIRST_NAMES)} {ran.choice(self.LAST_NAMES)}",
                age=ran.randint(18, 99),
                id=ran.choice(unique_ids),
            )
            for _ in range(100)
        ]
        self.buildings = [
            Building(
                address=f"{ran.randint(1, 999)} {ran.choice(self.STREET_NAMES)} {ran.choice(self.STREET_TYPES)}",
                owner=ran.choice(self.people),
                id=ran.choice(unique_ids),
            )
            for _ in range(20)
        ]
        self.cities = [
            City(
                name=f"{ran.choice(self.CITY_PARTS)}{ran.choice(self.CITY_SUFFIXES)}",
                buildings=[ran.choice(self.buildings) for _ in range(5)],
                governor=ran.choice(self.people),
                id=ran.choice(unique_ids),
            )
            for _ in range(10)
        ]
        self.regions = [
            Region(
                name=f"{ran.choice(self.CITY_PARTS)} County",
                cities=[ran.choice(self.cities) for _ in range(5)],
                id=ran.choice(unique_ids),
            )
            for _ in range(5)
        ]
        self.countries = [
            Country(
                name=f"{ran.choice(self.CITY_PARTS)}land",
                regions=[ran.choice(self.regions) for _ in range(5)],
                president=ran.choice(self.people),
                capital=ran.choice(self.cities),
                id=ran.choice(unique_ids),
            )
            for _ in range(2)
        ]

    def __repr__(self):
        return (
            f'<Data people={len(self.people)}, '
            f'buildings={len(self.buildings)}, '
            f'cities={len(self.cities)}, '
            f'regions={len(self.regions)}, '
            f'countries={len(self.countries)}> '
        )


data = Data()


@app.get("/people", response_model=List[Person])
async def get_people():
    return data.people


@app.get("/people/{person_id}", response_model=Person)
async def get_person(person_id: int):
    for person in data.people:
        if person.id == person_id:
            return person
    raise HTTPException(status_code=404, detail="Person not found")


@app.get("/openapi.json")
async def openapi():
    return app.openapi()


client = TestClient(app)

print(client.get("/people").json())
