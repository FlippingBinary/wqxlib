from .SimpleContent import (
  ElectronicAddressText,
  ElectronicAddressTypeName
)
from yattag import Doc

class ElectronicAddress:
  """A location within a system of worldwide electronic communication where a computer user can access information or receive electronic mail."""

  __electronicAddressText: ElectronicAddressText
  __electronicAddressTypeName: ElectronicAddressTypeName

  def __init__(self, o=None, *,
    electronicAddressText:ElectronicAddressText = None,
    electronicAddressTypeName:ElectronicAddressTypeName = None
  ):
    if isinstance(o, ElectronicAddress):
      # Assign attributes from object without typechecking
      self.__electronicAddressText = o.electronicAddressText
      self.__electronicAddressTypeName = o.electronicAddressTypeName
    elif isinstance(o, dict):
      # Assign attributes from dictionary with typechecking
      self.electronicAddressText = o.get('electronicAddressText', default = None)
      self.electronicAddressTypeName = o.get('electronicAddressTypeName', default = None)
    else:
      # Assign attributes from named keywords with typechecking
      self.electronicAddressText = electronicAddressText
      self.electronicAddressTypeName = electronicAddressTypeName

  @property
  def electronicAddressText(self) -> ElectronicAddressText:
    return self.__electronicAddressText
  @electronicAddressText.setter
  def electronicAddressText(self, val:ElectronicAddressText) -> None:
    self.__electronicAddressText = None if val is None else ElectronicAddressText(val)

  @property
  def electronicAddressTypeName(self) -> ElectronicAddressTypeName:
    return self.__electronicAddressTypeName
  @electronicAddressTypeName.setter
  def electronicAddressTypeName(self, val:ElectronicAddressTypeName) -> None:
    self.__electronicAddressTypeName = None if val is None else ElectronicAddressTypeName(val)

  def generateXML(self, name:str = 'ElectronicAddress') -> str:
    doc, tag, text, line = Doc().ttl()

    with tag(name):
      if self.__electronicAddressText is not None:
        line('ElectronicAddressText', self.__electronicAddressText)
      if self.__electronicAddressTypeName is not None:
        line('ElectronicAddressTypeName', self.__electronicAddressTypeName)

    return doc.getvalue()
