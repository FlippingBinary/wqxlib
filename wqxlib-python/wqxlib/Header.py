from datetime import datetime
from rfc3986 import uri_reference
from typing import List, Union
from yattag import Doc, indent
from .common import WQXException

class Header:
  __author: str
  __organization: str
  __title: str
  __creationTime: datetime
  __comment: str
  __dataService: str
  __contactInfo: str
  __notification: List[uri_reference]
  __sensitivity: str
  __property: dict

  def __init__(self, o=None, *,
    author = None,
    organization = None,
    title = None,
    creationTime = None,
    comment = None,
    dataService = None,
    contactInfo = None,
    notification = None,
    sensitivity = None,
    property = None
  ):
    if isinstance(o, Header):
      # Assign attributes from object without typechecking
      self.__author = o.author
      self.__organization = o.organization
      self.__title = o.title
      self.__creationTime = o.creationTime
      self.__comment = o.comment
      self.__dataService = o.dataService
      self.__contactInfo = o.contactInfo
      self.__notification = o.notification
      self.__sensitivity = o.sensitivity
      self.__property = o.property
    elif isinstance(o, dict):
      # Assign attributes from dictionary with typechecking
      self.author = o.get('author', default = None)
      self.organization = o.get('organization', default = None)
      self.title = o.get('title', default = None)
      self.creationTime = o.get('creationTime', default = None)
      self.comment = o.get('comment', default = None)
      self.dataService = o.get('dataService', default = None)
      self.contactInfo = o.get('contactInfo', default = None)
      self.notification = o.get('notification', default = None)
      self.sensitivity = o.get('sensitivity', default = None)
      # self.property is tricky because Python confuses it with the decorator
      property = o.get('property', default = None)
      if property is not None and not isinstance(property, dict):
        raise TypeError("Property 'property' must be a dict of 0 or more key/value pairs.")
      self.__property = {} if property is None else property
    else:
      # Assign attributes from named keywords with typechecking
      self.author = author
      self.organization = organization
      self.title = title
      self.creationTime = creationTime
      self.comment = comment
      self.dataService = dataService
      self.contactInfo = contactInfo
      self.notification = notification
      self.sensitivity = sensitivity
      # self.property is tricky because Python confuses it with the decorator
      if property is not None and not isinstance(property, dict):
        raise TypeError("Property 'property' must be a dict of 0 or more key/value pairs.")
      self.__property = {} if property is None else property

  @property
  def author(self) -> str:
    return self.__author
  @author.setter
  def author(self, val:str) -> None:
    self.__author = None if val is None else str(val)

  @property
  def organization(self) -> str:
    return self.__organization
  @organization.setter
  def organization(self, val:str) -> None:
    if not isinstance(val, str):
      raise TypeError("Property 'organization' must be a string.")
    if len(val) < 1:
      raise ValueError("Property 'organization is required.")
    self.__organization = None if val is None else str(val)

  @property
  def title(self) -> str:
    return self.__title
  @title.setter
  def title(self, val:str) -> None:
    if val is not None and not isinstance(val, str):
      raise TypeError("Property 'title' must be a string")
    self.__title = 'WQX' if val is None or len(val) < 1 else val

  @property
  def creationTime(self) -> datetime:
    return self.__creationTime
  @creationTime.setter
  def creationTime(self, val:datetime) -> None:
    if val is not None and not isinstance(val, datetime):
      raise TypeError("Property 'creationTime' must be a datetime.")
    self.__creationTime = datetime.now() if val is None else val

  @property
  def comment(self) -> str:
    return self.__comment
  @comment.setter
  def comment(self, val) -> None:
    if val is not None and not isinstance(val, str):
      raise TypeError("Property 'comment' must be a string, if provided.")
    self.__comment = None if val is None or len(val) < 1 else val

  @property
  def dataService(self) -> str:
    return self.__dataService
  @dataService.setter
  def dataService(self, val) -> None:
    if val is not None and not isinstance(val, str):
      raise TypeError("Property 'dataService' must be a string, if provided.")
    self.__dataService = None if val is None or len(val) < 1 else val

  @property
  def contactInfo(self) -> str:
    return self.__contactInfo
  @contactInfo.setter
  def contactInfo(self, val:str) -> None:
    self.__contactInfo = None if val is None else str(val)

  @property
  def notification(self) -> List[uri_reference]:
    return self.__notification
  @notification.setter
  def notification(self, val:Union[uri_reference,List[uri_reference]]) -> None:
    if val is None:
      self.__notification = []
    elif isinstance(val, list):
      r:List[str] = []
      for x in val:
        u = uri_reference(x)
        if not u.is_valid():
          raise WQXException("Attribute 'notification' must be a list of valid URIs, if provided.")
        r.append(u)
      self.__notification = r
    else:
      u = uri_reference(val)
      if not u.is_valid():
        raise WQXException("Attribute 'notification' must be a list of valid URIs, if provided.")
      self.__notification = [u]

  @property
  def sensitivity(self) -> str:
    return self.__sensitivity
  @sensitivity.setter
  def sensitivity(self, val) -> None:
    if val is not None and not isinstance(val, str):
      raise TypeError("Property 'sensitivity' must be a string, if provided.")
    self.__sensitivity = None if val is None or len(val) < 1 else val

  @property
  def property(self) -> dict:
    return self.__property
  @property.setter
  def property(self, val:dict) -> None:
    if val is not None and not isinstance(val, dict[str,str]):
      raise TypeError("Property 'property' must be a dict of 0 or more key/value pairs.")
    self.__property = {} if val is None else val

  def generateXML(self, name:str = 'Header') -> str:
    doc, tag, text, line = Doc().ttl()

    with tag(name):
      if self.__author is None:
        raise WQXException("Property 'author' is required.")
      line('Author', self.__author)
      if self.__organization is None:
        raise WQXException("Property 'organization' is required.")
      line('Organization', self.__organization)
      if self.__title is None:
        raise WQXException("Property 'title' is required.")
      line('Title', self.__title)
      if self.__creationTime is None:
        raise WQXException("Attribute 'creationTime' is required.")
      line('CreationTime', self.__creationTime.astimezone().replace(microsecond=0).isoformat())
      if self.__comment is not None:
        line('Comment', self.__comment)
      if self.__dataService is not None:
        line('DataService', self.__dataService)
      if self.__contactInfo is not None:
        line('ContactInfo', self.__contactInfo)
      for x in self.__notification:
        line('Notification', x.unsplit())
      if self.__sensitivity is not None:
        line('Sensitivity', self.__sensitivity)
      for key in self.__property:
        with tag('Property'):
          line('name', key)
          line('value', self.__property[key])

    return doc.getvalue()
