from typing import Dict, List

from pydantic import BaseModel


class GristColumn(BaseModel):
    id: str = ""
    fields: Dict = dict()


class GristTable(BaseModel):
    id: str = ""
    columns: List[GristColumn] = list()
