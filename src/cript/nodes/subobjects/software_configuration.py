from dataclasses import dataclass, field, replace
from typing import List, Union

from cript.nodes.core import BaseNode
from cript.nodes.subobjects.algorithm import Algorithm
from cript.nodes.subobjects.citation import Citation
from cript.nodes.subobjects.software import Software


class SoftwareConfiguration(BaseNode):
    """
    Software_Configuration Node
    """

    @dataclass(frozen=True)
    class JsonAttributes(BaseNode.JsonAttributes):
        software: Union[Software, None] = None
        algorithms: List[Algorithm] = field(default_factory=list)
        notes: str = ""
        citation: List[Citation] = field(default_factory=list)

    _json_attrs: JsonAttributes = JsonAttributes()

    def __init__(self, software: Software, algorithms: Union[List[Algorithm], None] = None, notes: str = "", citation: Union[List[Citation], None] = None, **kwargs):
        if algorithms is None:
            algorithms = []
        if citation is None:
            citation = []
        super().__init__(**kwargs)
        self._json_attrs = replace(self._json_attrs, software=software, algorithms=algorithms, notes=notes, citation=citation)
        self.validate()

    @property
    def software(self) -> Union[Software, None]:
        return self._json_attrs.software

    @software.setter
    def software(self, new_software: Union[Software, None]):
        new_attrs = replace(self._json_attrs, software=new_software)
        self._update_json_attrs_if_valid(new_attrs)

    @property
    def algorithms(self) -> List[Algorithm]:
        return self._json_attrs.algorithms.copy()

    @algorithms.setter
    def algorithms(self, new_algorithms: List[Algorithm]):
        new_attrs = replace(self._json_attrs, algorithms=new_algorithms)
        self._update_json_attrs_if_valid(new_attrs)

    @property
    def notes(self) -> str:
        return self._json_attrs.notes

    @notes.setter
    def notes(self, new_notes: str):
        new_attrs = replace(self._json_attrs, notes=new_notes)
        self._update_json_attrs_if_valid(new_attrs)

    @property
    def citation(self) -> List[Citation]:
        return self._json_attrs.citation.copy()

    @citation.setter
    def citation(self, new_citation: List[Citation]):
        new_attrs = replace(self._json_attrs, citation=new_citation)
        self._update_json_attrs_if_valid(new_attrs)
