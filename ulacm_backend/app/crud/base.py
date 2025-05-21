# File: ulacm_backend/app/crud/base.py
# Purpose: Base class for CRUD operations (optional, but can reduce boilerplate).

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func # For count

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base class for CRUD operations on a SQLAlchemy model.

    Attributes:
        model: The SQLAlchemy model class.
    """
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: A SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: The SQLAlchemy async session.
            id: The ID of the record to retrieve.

        Returns:
            The record if found, otherwise None.
        """
        statement = select(self.model).where(self.model.id == id) # Assumes 'id' as primary key name
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            db: The SQLAlchemy async session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            A list of records.
        """
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_multi_with_total_count(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, **filters: Any
    ) -> tuple[List[ModelType], int]:
        """
        Get multiple records with pagination and a total count of items matching filters.

        Args:
            db: The SQLAlchemy async session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            **filters: Keyword arguments for filtering (e.g., name="example").

        Returns:
            A tuple containing a list of records and the total count.
        """
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if filters:
            query = query.filter_by(**filters)
            count_query = count_query.filter_by(**filters)

        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar_one()

        items_result = await db.execute(query.offset(skip).limit(limit))
        items = items_result.scalars().all()

        return items, total_count


    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            db: The SQLAlchemy async session.
            obj_in: The Pydantic schema containing the data for the new record.

        Returns:
            The created record.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db: The SQLAlchemy async session.
            db_obj: The existing database object to update.
            obj_in: The Pydantic schema or dictionary containing the data to update.

        Returns:
            The updated record.
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) # Pydantic v2
            # update_data = obj_in.dict(exclude_unset=True) # Pydantic v1
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """
        Remove a record by ID.

        Args:
            db: The SQLAlchemy async session.
            id: The ID of the record to remove.

        Returns:
            The removed record if found and deleted, otherwise None.
        """
        statement = select(self.model).where(self.model.id == id) # Assumes 'id' as PK
        result = await db.execute(statement)
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
