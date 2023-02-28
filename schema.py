import sys
sys.path.insert(0, "/home/evan/code/rubydex_subgraph")
import typing
import strawberry
from dataclasses import dataclass, field
from typing import List, Optional, TypeVar, Union
from subgraph.resolver import Query


schema = strawberry.Schema(query=Query)