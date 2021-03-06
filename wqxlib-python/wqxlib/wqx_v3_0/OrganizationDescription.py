from ..common import WQXException
from .SimpleContent import (
  OrganizationDescriptionText,
  OrganizationFormalName,
  OrganizationIdentifier,
  TribalCode
)
from yattag import Doc

class OrganizationDescription:
  """The particular word(s) regularly connected with a unique framework of authority within which a person or persons act, or are designated to act, towards some purpose."""

  __organizationIdentifier: OrganizationIdentifier
  __organizationFormalName: OrganizationFormalName
  __organizationDescriptionText: OrganizationDescriptionText
  __tribalCode: TribalCode

  def __init__(self, o=None, *,
    organizationIdentifier:OrganizationIdentifier = None,
    organizationFormalName:OrganizationFormalName = None,
    organizationDescriptionText:OrganizationDescriptionText = None,
    tribalCode:TribalCode = None
  ):
    if isinstance(o, OrganizationDescription):
      # Assign attributes from object without typechecking
      self.__organizationIdentifier = o.organizationIdentifier
      self.__organizationFormalName = o.organizationFormalName
      self.__organizationDescriptionText = o.organizationDescriptionText
      self.__tribalCode = o.tribalCode
    elif isinstance(o, dict):
      # Assign attributes from dictionary with typechecking
      self.organizationIdentifier = o.get('organizationIdentifier', default = None)
      self.organizationFormalName = o.get('organizationFormalName', default = None)
      self.organizationDescriptionText = o.get('organizationDescriptionText', default = None)
      self.tribalCode = o.get('tribalCode', default = None)
    else:
      # Assign attributes from named keywords with typechecking
      self.organizationIdentifier = organizationIdentifier
      self.organizationFormalName = organizationFormalName
      self.organizationDescriptionText = organizationDescriptionText
      self.tribalCode = tribalCode

  @property
  def organizationIdentifier(self) -> OrganizationIdentifier:
    return self.__organizationIdentifier
  @organizationIdentifier.setter
  def organizationIdentifier(self, val:OrganizationIdentifier) -> None:
    self.__organizationIdentifier = OrganizationIdentifier(val)

  @property
  def organizationFormalName(self) -> OrganizationFormalName:
    return self.__organizationFormalName
  @organizationFormalName.setter
  def organizationFormalName(self, val:OrganizationFormalName) -> None:
    self.__organizationFormalName = OrganizationFormalName(val)

  @property
  def organizationDescriptionText(self) -> OrganizationDescriptionText:
    return self.__organizationDescriptionText
  @organizationDescriptionText.setter
  def organizationDescriptionText(self, val:OrganizationDescriptionText) -> None:
    self.__organizationDescriptionText = None if val is None else OrganizationDescriptionText(val)

  @property
  def tribalCode(self) -> TribalCode:
    return self.__tribalCode
  @tribalCode.setter
  def tribalCode(self, val:TribalCode) -> None:
    self.__tribalCode = None if val is None else TribalCode(val)

  def generateXML(self, name:str = 'OrganizationDescription') -> str:
    doc, tag, text, line = Doc().ttl()

    with tag(name):
      if self.organizationIdentifier is None:
        raise WQXException("Attribute 'organizationIdentifier' is required.")
      line('OrganizationIdentifier', self.__organizationIdentifier)
      if self.organizationFormalName is None:
        raise WQXException("Attribute 'organizationFormalName' is required.")
      line('OrganizationFormalName', self.__organizationFormalName)
      if self.__organizationDescriptionText is not None:
        line('OrganizationDescriptionText', self.__organizationDescriptionText)
      if self.__tribalCode is not None:
        line('TribalCode', self.__tribalCode)

    return doc.getvalue()
