from pydantic import BaseModel
from typing import Dict, List


class GristColumn(BaseModel):
    id: str = ""
    fields: Dict = dict()


class GristTable(BaseModel):
    id: str = ""
    columns: List[GristColumn] = list()
