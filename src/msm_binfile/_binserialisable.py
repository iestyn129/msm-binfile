from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
	from ._binfile import BinFile
else:
	BinFile = object

__all__: list[str] = ['BinSerializable']


class BinSerializable(ABC):
	@classmethod
	@abstractmethod
	def read(cls, bf: BinFile) -> Self: ...

	@classmethod
	@abstractmethod
	def from_dict(cls, data: dict) -> Self: ...

	@abstractmethod
	def write(self, bf: BinFile) -> None: ...

	@abstractmethod
	def to_dict(self) -> dict: ...
