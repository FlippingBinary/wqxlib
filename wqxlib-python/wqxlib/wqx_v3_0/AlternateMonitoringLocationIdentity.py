from ..common import WQXException
from .SimpleContent import (
  MonitoringLocationIdentifier,
  MonitoringLocationIdentifierContext
)
from yattag import Doc

class AlternateMonitoringLocationIdentity:
  """Alternate identifications of a monitoring location."""

  __monitoringLocationIdentifier: MonitoringLocationIdentifier
  __monitoringLocationIdentifierContext: MonitoringLocationIdentifierContext

  def __init__(self, o=None, *,
    monitoringLocationIdentifier:MonitoringLocationIdentifier = None,
    monitoringLocationIdentifierContext:MonitoringLocationIdentifierContext = None
  ):
    if isinstance(o, AlternateMonitoringLocationIdentity):
      # Assign attributes from object without typechecking
      self.__monitoringLocationIdentifier = o.monitoringLocationIdentifier
      self.__monitoringLocationIdentifierContext = o.monitoringLocationIdentifierContext
    elif isinstance(o, dict):
      # Assign attributes from dictionary with typechecking
      self.monitoringLocationIdentifier = o.get('monitoringLocationIdentifier', default = None)
      self.monitoringLocationIdentifierContext = o.get('monitoringLocationIdentifierContext', default = None)
    else:
      # Assign attributes from named keywords with typechecking
      self.monitoringLocationIdentifier = monitoringLocationIdentifier
      self.monitoringLocationIdentifierContext = monitoringLocationIdentifierContext

  @property
  def monitoringLocationIdentifier(self) -> MonitoringLocationIdentifier:
    return self.__monitoringLocationIdentifier
  @monitoringLocationIdentifier.setter
  def monitoringLocationIdentifier(self, val:MonitoringLocationIdentifier) -> None:
    self.__monitoringLocationIdentifier = MonitoringLocationIdentifier(val)

  @property
  def monitoringLocationIdentifierContext(self) -> MonitoringLocationIdentifierContext:
    return self.__monitoringLocationIdentifierContext
  @monitoringLocationIdentifierContext.setter
  def monitoringLocationIdentifierContext(self, val:MonitoringLocationIdentifierContext) -> None:
    self.__monitoringLocationIdentifierContext = MonitoringLocationIdentifierContext(val)

  def generateXML(self, name:str = 'AlternateMonitoringLocationIdentity') -> str:
    doc, tag, text, line = Doc().ttl()

    with tag(name):
      if self.__monitoringLocationIdentifier is None:
        raise WQXException("Attribute 'MonitoringLocationIdentifier' is required.")
      line('MonitoringLocationIdentifier', self.__monitoringLocationIdentifier)
      if self.__monitoringLocationIdentifierContext is None:
        raise WQXException("Attribute 'MonitoringLocationIdentifierContext' is required.")
      line('MonitoringLocationIdentifierContext', self.__monitoringLocationIdentifierContext)

    return doc.getvalue()
