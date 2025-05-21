# File: ulacm_backend/app/db/base_class.py
# Purpose: Base class for SQLAlchemy ORM models.
# Corrected: Updated import location for as_declarative and declared_attr

from typing import Any
# from sqlalchemy.ext.declarative import as_declarative, declared_attr # Deprecated import
from sqlalchemy.orm import as_declarative, declared_attr # Correct import for SQLAlchemy >= 2.0
from sqlalchemy import inspect

@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.
    It provides a default __tablename__ and id primary key column.
    """
    id: Any # type: ignore # Assuming primary key might vary, Any avoids specific type need here
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s" # e.g., Team -> teams

    def _asdict(self) -> dict:
        """Return a dictionary representation of the model."""
        # Ensure the instance is bound to ORM state before inspecting
        if not inspect(self).has_identity:
             # Handle cases where the object is not yet persistent or mapped if needed
             # For a simple dict representation, accessing attributes directly might be safer
             # return {key: getattr(self, key) for key in self.__dict__ if not key.startswith('_')} # Alternative naive approach
             # Sticking with inspect for mapped columns, assuming it's called on managed objects
             pass # Or return empty dict {} if inspection fails for transient objects

        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}
