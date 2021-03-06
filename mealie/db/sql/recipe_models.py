import datetime
from datetime import date
from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy.ext.orderinglist import ordering_list


class ApiExtras(SqlAlchemyBase):
    __tablename__ = "api_extras"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    key_name = sa.Column(sa.String, unique=True)
    value = sa.Column(sa.String)

    def __init__(self, key, value) -> None:
        self.key_name = key
        self.value = value

    def dict(self):
        return {self.key_name: self.value}


class Category(SqlAlchemyBase):
    __tablename__ = "categories"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    name = sa.Column(sa.String, index=True)

    def to_str(self):
        return self.name


class Tag(SqlAlchemyBase):
    __tablename__ = "tags"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    name = sa.Column(sa.String, index=True)

    def to_str(self):
        return self.name


class Note(SqlAlchemyBase):
    __tablename__ = "notes"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)

    def __init__(self, title, text) -> None:
        self.title = title
        self.text = text

    def dict(self):
        return {"title": self.title, "text": self.text}


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = "recipes_ingredients"
    id = sa.Column(sa.Integer, primary_key=True)
    position = sa.Column(sa.Integer)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    ingredient = sa.Column(sa.String)

    def update(self, ingredient):
        self.ingredient = ingredient

    def to_str(self):
        return self.ingredient


class RecipeInstruction(SqlAlchemyBase):
    __tablename__ = "recipe_instructions"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    position = sa.Column(sa.Integer)
    type = sa.Column(sa.String, default="")
    text = sa.Column(sa.String)

    def dict(self):
        data = {"@type": self.type, "text": self.text}

        return data


class RecipeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes"
    # Database Specific
    id = sa.Column(sa.Integer, primary_key=True)

    # General Recipe Properties
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    image = sa.Column(sa.String)
    recipeYield = sa.Column(sa.String)
    recipeIngredient: List[RecipeIngredient] = orm.relationship(
        "RecipeIngredient",
        cascade="all, delete",
        order_by="RecipeIngredient.position",
        collection_class=ordering_list("position"),
    )
    recipeInstructions: List[RecipeInstruction] = orm.relationship(
        "RecipeInstruction",
        cascade="all, delete",
        order_by="RecipeInstruction.position",
        collection_class=ordering_list("position"),
    )

    # How to Properties
    totalTime = sa.Column(sa.String)
    prepTime = sa.Column(sa.String)
    performTime = sa.Column(sa.String)

    # Mealie Specific
    slug = sa.Column(sa.String, index=True, unique=True)
    categories: List[Category] = orm.relationship(
        "Category",
        cascade="all, delete",
    )
    tags: List[Tag] = orm.relationship(
        "Tag",
        cascade="all, delete",
    )
    dateAdded = sa.Column(sa.Date, default=date.today)
    notes: List[Note] = orm.relationship(
        "Note",
        cascade="all, delete",
    )
    rating = sa.Column(sa.Integer)
    orgURL = sa.Column(sa.String)
    extras: List[ApiExtras] = orm.relationship("ApiExtras", cascade="all, delete")

    def __init__(
        self,
        name: str = None,
        description: str = None,
        image: str = None,
        recipeYield: str = None,
        recipeIngredient: List[str] = None,
        recipeInstructions: List[dict] = None,
        totalTime: str = None,
        prepTime: str = None,
        performTime: str = None,
        slug: str = None,
        categories: List[str] = None,
        tags: List[str] = None,
        dateAdded: datetime.date = None,
        notes: List[dict] = None,
        rating: int = None,
        orgURL: str = None,
        extras: dict = None,
    ) -> None:
        self.name = name
        self.description = description
        self.image = image
        self.recipeYield = recipeYield
        self.recipeIngredient = [
            RecipeIngredient(ingredient=ingr) for ingr in recipeIngredient
        ]
        self.recipeInstructions = [
            RecipeInstruction(text=instruc.get("text"), type=instruc.get("text"))
            for instruc in recipeInstructions
        ]
        self.totalTime = totalTime
        self.prepTime = prepTime
        self.performTime = performTime

        # Mealie Specific
        self.slug = slug
        self.categories = [Category(name=cat) for cat in categories]
        self.tags = [Tag(name=tag) for tag in tags]
        self.dateAdded = dateAdded
        self.notes = [Note(**note) for note in notes]
        self.rating = rating
        self.orgURL = orgURL
        self.extras = [ApiExtras(key=key, value=value) for key, value in extras.items()]

    def update(
        self,
        session,
        name: str = None,
        description: str = None,
        image: str = None,
        recipeYield: str = None,
        recipeIngredient: List[str] = None,
        recipeInstructions: List[dict] = None,
        totalTime: str = None,
        prepTime: str = None,
        performTime: str = None,
        slug: str = None,
        categories: List[str] = None,
        tags: List[str] = None,
        dateAdded: datetime.date = None,
        notes: List[dict] = None,
        rating: int = None,
        orgURL: str = None,
        extras: dict = None,
    ):
        """Updated a database entry by removing nested rows and rebuilds the row through the __init__ functions"""
        list_of_tables = [RecipeIngredient, RecipeInstruction, Category, Tag, ApiExtras]
        RecipeModel._sql_remove_list(session, list_of_tables, self.id)

        self.__init__(
            name=name,
            description=description,
            image=image,
            recipeYield=recipeYield,
            recipeIngredient=recipeIngredient,
            recipeInstructions=recipeInstructions,
            totalTime=totalTime,
            prepTime=prepTime,
            performTime=performTime,
            slug=slug,
            categories=categories,
            tags=tags,
            dateAdded=dateAdded,
            notes=notes,
            rating=rating,
            orgURL=orgURL,
            extras=extras,
        )

    def dict(self):
        data = {
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "recipeYield": self.recipeYield,
            "recipeIngredient": [x.to_str() for x in self.recipeIngredient],
            "recipeInstructions": [x.dict() for x in self.recipeInstructions],
            "totalTime": self.totalTime,
            "prepTime": self.prepTime,
            "performTime": self.performTime,
            # Mealie
            "slug": self.slug,
            "categories": [x.to_str() for x in self.categories],
            "tags": [x.to_str() for x in self.tags],
            "dateAdded": self.dateAdded,
            "notes": [x.dict() for x in self.notes],
            "rating": self.rating,
            "orgURL": self.orgURL,
            "extras": RecipeModel._flatten_dict(self.extras),
        }

        return data
