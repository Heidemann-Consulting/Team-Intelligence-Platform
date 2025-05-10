# File: ulacm_backend/app/crud/__init__.py
# Purpose: Makes CRUD modules available for easier import.

from .base import CRUDBase
from .crud_team import team
from .crud_content_item import content_item
from .crud_content_version import content_version
from . import crud_search # Import the module itself
