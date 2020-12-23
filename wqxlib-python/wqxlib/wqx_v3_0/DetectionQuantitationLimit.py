from yattag import Doc, indent
from .MeasureCompact import MeasureCompact
from .SimpleContent import (
  DetectionQuantitationLimitTypeName,
  DetectionQuantitationLimitCommentText,
)
from ..common import WQXException

class DetectionQuantitationLimit:
  """Information that describes one of a variety of detection or quantitation limits determined in a laboratory."""

  __detectionQuantitationLimitTypeName: DetectionQuantitationLimitTypeName
  __detectionQuantitationLimitMeasure: MeasureCompact
  __detectionQuantitationLimitCommentText: DetectionQuantitationLimitCommentText

  def __init__(self):
    self.__detectionQuantitationLimitTypeName = None
    self.__detectionQuantitationLimitMeasure = None
    self.__detectionQuantitationLimitCommentText = None

  @property
  def detectionQuantitationLimitTypeName(self) -> DetectionQuantitationLimitTypeName:
    return self.__detectionQuantitationLimitTypeName
  @detectionQuantitationLimitTypeName.setter
  def detectionQuantitationLimitTypeName(self, val:DetectionQuantitationLimitTypeName) -> None:
    self.__detectionQuantitationLimitTypeName = DetectionQuantitationLimitTypeName(val)

  @property
  def detectionQuantitationLimitMeasure(self) -> MeasureCompact:
    return self.__detectionQuantitationLimitMeasure
  @detectionQuantitationLimitMeasure.setter
  def detectionQuantitationLimitMeasure(self, val:MeasureCompact) -> None:
    self.__detectionQuantitationLimitMeasure = MeasureCompact(val)

  @property
  def detectionQuantitationLimitCommentText(self) -> DetectionQuantitationLimitCommentText:
    return self.__detectionQuantitationLimitCommentText
  @detectionQuantitationLimitCommentText.setter
  def detectionQuantitationLimitCommentText(self, val:DetectionQuantitationLimitCommentText) -> None:
    self.__detectionQuantitationLimitCommentText = None if val is None else DetectionQuantitationLimitCommentText(val)

  def generateXML(self):
    if self.__detectionQuantitationLimitTypeName is None:
      raise WQXException("Attribute 'detectionQuantitationLimitTypeName' is required.")
    if self.__detectionQuantitationLimitMeasure is None:
      raise WQXException("Attribute 'detectionQuantitationLimitMeasure' is required.")

    doc, tag, text, line = Doc().ttl()

    line('DetectionQuantitationLimitTypeName', self.__detectionQuantitationLimitTypeName)
    with tag('MeasureCompact'):
      doc.asis(self.__detectionQuantitationLimitMeasure.generateXML())
    if self.__detectionQuantitationLimitCommentText is not None:
      line('DetectionQuantitationLimitCommentText', self.__detectionQuantitationLimitCommentText)

    return indent(doc.getvalue(), indentation = ' '*2)