from yattag import Doc, indent
from .SimpleContent import *
from ..common import WQXException

class OrganizationDescription:
  """The particular word(s) regularly connected with a unique framework of authority within which a person or persons act, or are designated to act, towards some purpose."""

  __organizationIdentifier: OrganizationIdentifier
  __organizationFormalName: OrganizationFormalName
  __organizationDescriptionText: OrganizationDescriptionText
  __tribalCode: TribalCode

  def __init__(self,
    organizationIdentifier = None,
    organizationFormalName = None,
    organizationDescriptionText = None,
    tribalCode = None
  ):
    self.__organizationIdentifier = organizationIdentifier
    self.__organizationFormalName = organizationFormalName
    self.__organizationDescriptionText = organizationDescriptionText
    self.__tribalCode = tribalCode

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

  def generateXML(self):
    if self.organizationIdentifier is None:
      raise WQXException("Attribute 'organizationIdentifier' is required.")
    if self.organizationFormalName is None:
      raise WQXException("Attribute 'organizationFormalName' is required.")

    doc, tag, text, line = Doc().ttl()

    line('OrganizationIdentifier', self.__organizationIdentifier)
    line('OrganizationFormalName', self.__organizationFormalName)
    if self.__organizationDescriptionText is not None:
      line('OrganizationDescriptionText', self.__organizationDescriptionText)
    if self.__tribalCode is not None:
      line('TribalCode', self.__tribalCode)

    return indent(doc.getvalue(), indentation = ' '*2)