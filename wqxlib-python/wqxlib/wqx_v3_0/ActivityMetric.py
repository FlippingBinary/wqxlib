from ..common import WQXException
from .ActivityMetricType import ActivityMetricType
from .MeasureCompact import MeasureCompact
from .SimpleContent import (
  CommentText,
  IndexIdentifier,
  MetricSamplingPointPlaceInSeries,
  MetricScore
)
from typing import List, Union
from yattag import Doc

class ActivityMetric:
  """This section allows for the reporting of metrics to support habitat or biotic integrity indices."""

  __activityMetricType: ActivityMetricType
  __metricValueMeasure: MeasureCompact
  __metricScore: MetricScore
  __metricSamplingPointPlaceInSeries: MetricSamplingPointPlaceInSeries
  __metricCommentText: CommentText
  __indexIdentifier: List[IndexIdentifier]

  def __init__(self, o=None, *,
    activityMetricType:ActivityMetricType = None,
    metricValueMeasure:MeasureCompact = None,
    metricScore:MetricScore = None,
    metricSamplingPointPlaceInSeries:MetricSamplingPointPlaceInSeries = None,
    metricCommentText:CommentText = None,
    indexIdentifier:IndexIdentifier = None
  ):
    if isinstance(o, ActivityMetric):
      # Assign attributes from object without typechecking
      self.__activityMetricType = o.activityMetricType
      self.__metricValueMeasure = o.metricValueMeasure
      self.__metricScore = o.metricScore
      self.__metricSamplingPointPlaceInSeries = o.metricSamplingPointPlaceInSeries
      self.__metricCommentText = o.metricCommentText
      self.__indexIdentifier = o.indexIdentifier
    elif isinstance(o, dict):
      # Assign attributes from dictionary with typechecking
      self.activityMetricType = o.get('activityMetricType', default = None)
      self.metricValueMeasure = o.get('metricValueMeasure', default = None)
      self.metricScore = o.get('metricScore', default = None)
      self.metricSamplingPointPlaceInSeries = o.get('metricSamplingPointPlaceInSeries', default = None)
      self.metricCommentText = o.get('metricCommentText', default = None)
      self.indexIdentifier = o.get('indexIdentifier', default = None)
    else:
      # Assign attributes from named keywords with typechecking
      self.activityMetricType = activityMetricType
      self.metricValueMeasure = metricValueMeasure
      self.metricScore = metricScore
      self.metricSamplingPointPlaceInSeries = metricSamplingPointPlaceInSeries
      self.metricCommentText = metricCommentText
      self.indexIdentifier = indexIdentifier

  @property
  def activityMetricType(self) -> ActivityMetricType:
    return self.__activityMetricType
  @activityMetricType.setter
  def activityMetricType(self, val:ActivityMetricType) -> None:
    self.__activityMetricType = None if val is None else ActivityMetricType(val)

  @property
  def metricValueMeasure(self) -> MeasureCompact:
    """A non-scaled value calculated from raw results that may be scaled into a metric score."""
    return self.__metricValueMeasure
  @metricValueMeasure.setter
  def metricValueMeasure(self, val:MeasureCompact) -> None:
    """A non-scaled value calculated from raw results that may be scaled into a metric score."""
    self.__metricValueMeasure = None if val is None else MeasureCompact(val)

  @property
  def metricScore(self) -> MetricScore:
    return self.__metricScore
  @metricScore.setter
  def metricScore(self, val:MetricScore) -> None:
    self.__metricScore = None if val is None else MetricScore(val)

  @property
  def metricSamplingPointPlaceInSeries(self) -> MetricSamplingPointPlaceInSeries:
    return self.__metricSamplingPointPlaceInSeries
  @metricSamplingPointPlaceInSeries.setter
  def metricSamplingPointPlaceInSeries(self, val:MetricSamplingPointPlaceInSeries):
    self.__metricSamplingPointPlaceInSeries = None if val is None else MetricSamplingPointPlaceInSeries(val)

  @property
  def metricCommentText(self) -> CommentText:
    """Free text with general comments concerning the metric."""
    return self.__metricCommentText
  @metricCommentText.setter
  def metricCommentText(self, val:CommentText) -> None:
    """Free text with general comments concerning the metric."""
    self.__metricCommentText = None if val is None else CommentText(val)

  @property
  def indexIdentifier(self) -> IndexIdentifier:
    return self.__indexIdentifier
  @indexIdentifier.setter
  def indexIdentifier(self, val:Union[IndexIdentifier,List[IndexIdentifier]]) -> None:
    if val is None:
      self.__indexIdentifier = []
    elif isinstance(val, list):
      r:List[IndexIdentifier] = []
      for x in val:
        r.append(IndexIdentifier(x))
      self.__indexIdentifier = r
    else:
      self.__indexIdentifier = [IndexIdentifier(val)]

  def generateXML(self, name:str = 'ActivityMetric') -> str:
    doc, tag, text, line = Doc().ttl()

    with tag(name):
      if self.__activityMetricType is None:
        raise WQXException("Attribute 'activityMetricType' is required.")
      doc.asis(self.__activityMetricType.generateXML('ActivityMetricType'))
      if self.__metricValueMeasure is not None:
        doc.asis(self.__metricValueMeasure.generateXML('MetricValueMeasure'))
      if self.__metricScore is None:
        raise WQXException("Attribute 'metricScore' is required.")
      line('MetricScore', self.__metricScore)
      if self.__metricSamplingPointPlaceInSeries is not None:
        line('MetricSamplingPointPlaceInSeries',self.__metricSamplingPointPlaceInSeries)
      if self.__metricCommentText is not None:
        line('MetricCommentText', self.__metricCommentText)
      for x in self.__indexIdentifier:
        line('IndexIdentifier', x)

    return doc.getvalue()
