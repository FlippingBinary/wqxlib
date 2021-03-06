from collections import Counter
import re
from typing import List, Union
from yattag import Doc, indent
from .Header import Header
from .Payload import Payload
from .common import WQXException

class ID(str):
  """The type ID is used for an attribute that uniquely identifies an element in an XML document. An ID value must be an NCName. This means that it must start with a letter or underscore, and can only contain letters, digits, underscores, hyphens, and periods."""

  __pattern = re.compile(r"^[:A-Z_a-z\xC0-\xD6\xD8-\xF6\xF8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][-:0-9.A-Z_a-z\xC0-\xD6\xD8-\xF6\xF8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\xB7\u0300-\u036F\u203F-\u2040]*$")
  def __init__(self, o=None):
    if not isinstance(o, str) or re.match(self.__pattern, o):
      raise ValueError("Attribute of type 'ID' must be a valid XML Identifier.")

class Document:
  """The base document type used for submission to WQXWeb."""

  __id: ID
  __header: Header
  __payload: List[Payload]

  def __init__(self, o=None, *,
    id:ID = None,
    header:Header = None,
    payload:List[Payload] = None
  ):
    if isinstance(o, Document):
      # Assign attributes from object without typechecking
      self.__id = o.id
      self.__header = o.header
      self.__payload = o.payload
    elif isinstance(o, dict):
      # Assign attributes from dictionary with typechecking
      self.id = o.get('id', default = None)
      self.header = o.get('header', default = None)
      self.payload = o.get('payload', default = None)
    else:
      # Assign attributes from named keywords with typechecking
      self.header = header
      self.id = id
      self.payload = payload

  @property
  def header(self) -> Header:
    return self.__header
  @header.setter
  def header(self, val:Header) -> None:
    self.__header = None if val is None else Header(val)

  @property
  def id(self) -> ID:
    return self.__id
  @id.setter
  def id(self, val:ID) -> None:
    self.__id = ID(val)

  @property
  def payload(self) -> List[Payload]:
    return self.__payload
  @payload.setter
  def payload(self, val:Union[Payload,List[Payload]]) -> None:
    if val is None:
      self.__payload = []
    elif isinstance(val, list):
      r:List[Payload] = []
      for x in val:
        r.append(Payload(x))
      self.__payload = r
    else:
      self.__payload = [Payload(val)]

  def list_data_rule_violations(self) -> List[str]:
    """List all data rule (not XSD rules) violations of the enclosed Document.
    This function returns an empty list if none of the tests fail, but that does
    not guarantee the data will be accepted by WQX."""
    violations:List[str] = []

    for payload in self.__payload:
      if payload.operation != payload.UPDATE_INSERT:
        # Data rules only apply for Update-Insert operations
        continue

      data_rule_1 = """
        Data Rule #1: When ElectronicAddressText or ElectronicAddressTypeName is reported, both must be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.electronicAddress is not None )
      ):
        for electronic_address in payload.wqx.organization.electronicAddress:
          if (
            ( electronic_address.electronicAddressText is not None and electronic_address.electronicAddressTypeName is None ) or
            ( electronic_address.electronicAddressText is None and electronic_address.electronicAddressTypeName is not None )
          ):
            violations.append(data_rule_1.strip())

      data_rule_2 = """
        Data Rule #2: When TelephoneNumberText or TelephoneNumberTypeName is reported, both must be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.telephonic is not None )
      ):
        for telephonic in payload.wqx.organization.telephonic:
          if (
            ( telephonic.telephoneNumberText is not None and telephonic.telephoneNumberTypeName is None ) or
            ( telephonic.telephoneNumberText is None and telephonic.telephoneNumberTypeName is not None )
          ):
            violations.append(data_rule_2.strip())

      data_rule_3 = """
        Data Rule #3: When AddressText or AddressTypeName is reported, both must be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.organizationAddress is not None )
      ):
        for organization_address in payload.wqx.organization.organizationAddress:
          if (
            ( organization_address.addressText is not None and organization_address.addressTypeName is None ) or
            ( organization_address.addressText is None and organization_address.addressTypeName is not None )
          ):
            violations.append(data_rule_3.strip())
      
      data_rule_4 = """
        When HorizonitalCollectionMethodName is “Interpolation-Map”, SourceMapScaleNumeric must be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        if payload.wqx.organization.activity is not None:
          for activity in payload.wqx.organization.activity:
            if (
              ( activity.activityLocation is not None ) and
              ( activity.activityLocation.sourceMapScale is None ) and
              ( activity.activityLocation.horizontalCollectionMethodName == 'Interpolation-Map' )
            ):
              violations.append(data_rule_4.strip())
        if payload.wqx.organization.monitoringLocation is not None:
          for monitoring_location in payload.wqx.organization.monitoringLocation:
            if (
              ( monitoring_location.monitoringLocationGeospatial is not None ) and
              ( monitoring_location.monitoringLocationGeospatial.sourceMapScale is None ) and
              ( monitoring_location.monitoringLocationGeospatial.horizontalCollectionMethodName == 'Interpolation-Map' )
            ):
              violations.append(data_rule_4.strip())

      data_rule_5 = """
        When VerticalMeasure's MeasureValue is reported, the following also must be reported:
        VerticalMeasure's MeasureUnitCode,
        VerticalCollectionMethodName,
        VerticalCoordinateReferenceSystemDatumName.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.monitoringLocation is not None )
      ):
        for monitoring_location in payload.wqx.organization.monitoringLocation:
          if (
            ( monitoring_location.monitoringLocationGeospatial is not None ) and
            ( monitoring_location.monitoringLocationGeospatial.verticalMeasure is not None ) and
            ( monitoring_location.monitoringLocationGeospatial.verticalMeasure.measureValue is not None ) and
            (
              ( monitoring_location.monitoringLocationGeospatial.verticalMeasure.measureUnitCode is None ) or
              ( monitoring_location.monitoringLocationGeospatial.verticalCollectionMethodName is None ) or
              ( monitoring_location.monitoringLocationGeospatial.verticalCoordinateReferenceSystemDatumName is None )
            )
          ):
            violations.append(data_rule_5.strip())

      data_rule_6 = """
        Either ProjectDescriptionText or Project's AttachedBinaryObject must be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.project is not None )
      ):
        for project in payload.wqx.organization.project:
          if (
            ( project.projectDescriptionText is None ) and
            ( len (project.attachedBinaryObject) < 1 )
          ):
            violations.append(data_rule_6.strip())

      data_rule_7 = """
        Activity Depth/Height can be reported in only one of the following two ways (but not both):
        a. Specific depth using ActivityDepthHeightMeasure's MeasureValue.
        b. Depth Range using ActivityTopDepthHeightMeasure's MeasureValue and
        ActivityBottomDepthHeightMeasure's MeasureValue.
          i. This method must be used when ActivityTypeCode is “Sample-Integrated Vertical Profile”.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.activityDescription is not None ) and
            ( activity.activityDescription.activityDepthHeightMeasure is not None ) and
            ( activity.activityDescription.activityDepthHeightMeasure.measureValue is not None ) and
            (
              ( activity.activityDescription.activityTypeCode == 'Sample-Integrated Vertical Profile' ) or
              (
                ( activity.activityDescription.activityTopDepthHeightMeasure is not None ) and
                ( activity.activityDescription.activityTopDepthHeightMeasure.measureValue is not None )
              ) or (
                ( activity.activityDescription.activityBottomDepthHeightMeasure is not None ) and
                ( activity.activityDescription.activityBottomDepthHeightMeasure.measureValue is not None )
              )
            )
          ):
            violations.append(data_rule_7.strip())
  
      data_rule_8 = """
        When ActivityTypeCode contains the word 'Logger', DataLoggerLineName must be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.activityDescription is not None ) and
            ( activity.activityDescription.activityTypeCode is not None ) and
            ( 'Logger' in activity.activityDescription.activityTypeCode )
          ):
            for result in activity.result:
              if result.resultDescription.dataLoggerLineName is None:
                violations.append(data_rule_8.strip())

      data_rule_9 = """
        When ActivityMediaName is "Tissue" then BiologicalIntentName must also be "Tissue" (and visa-versa)
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          for result in activity.result:
            if (
              (
                ( activity.activityDescription is not None ) and
                ( activity.activityDescription.activityMediaName ) and
                ( 'Tissue' != activity.activityDescription.activityMediaName ) and
                ( result.biologicalResultDescription is not None ) and
                ( result.biologicalResultDescription.biologicalIntentName is not None ) and
                ( 'Tissue' == result.biologicalResultDescription.biologicalIntentName )
              ) or
              (
                ( activity.activityDescription is not None ) and
                ( activity.activityDescription.activityMediaName ) and
                ( 'Tissue' == activity.activityDescription.activityMediaName ) and
                ( result.biologicalResultDescription is not None ) and
                ( result.biologicalResultDescription.biologicalIntentName is not None ) and
                ( 'Tissue' != result.biologicalResultDescription.biologicalIntentName )
              )
            ):
              violations.append(data_rule_9.strip())

      data_rule_10 = """
        When ActivityMediaName (or BiologicalIntentName) is "Tissue", then SampleTissueAnatomyName must be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          for result in activity.result:
            if (
              ( activity.activityDescription is not None ) and
              ( activity.activityDescription.activityMediaName is not None ) and
              ( 'Tissue' == activity.activityDescription.activityMediaName ) and
              ( result.biologicalResultDescription is not None ) and
              ( result.biologicalResultDescription.biologicalIntentName is not None ) and
              ( 'Tissue' == result.biologicalResultDescription.biologicalIntentName )
            ):
              if result.biologicalResultDescription.sampleTissueAnatomyName is None:
                violations.append(data_rule_10.strip())

      data_rule_11 = """
        When ActivityMediaName is "Biological" then AssemblageSampledName must be reported
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.activityDescription is not None ) and
            ( activity.activityDescription.activityMediaName is not None ) and
            ( 'Biological' == activity.activityDescription.activityMediaName ) and
            (
              ( activity.biologicalActivityDescription is None ) or
              ( activity.biologicalActivityDescription.assemblageSampledName is None )
            )
          ):
            violations.append(data_rule_11.strip())

      data_rule_12 = """
        When ResultDetectionConditionText is 'Not Detected', 'Present Above Quantification Limit' or 'Present Below
        Quantification Limit', then DetectionQuantitationLimitTypeName and DetectionQuantitationLimitMeasure must be
        reported.
        """
      data_rule_12_pattern_1 = ['Not Detected', 'Present Above Quantification Limit', 'Present Below Quantification Limit']
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity )
      ):
        for activity in payload.wqx.organization.activity:
          for result in activity.result:
            if (
              ( result.resultDescription is not None ) and
              ( result.resultDescription.resultDetectionConditionText in data_rule_12_pattern_1 ) and
              ( not any(i.detectionQuantitationLimitTypeName is not None and i.detectionQuantitationLimitMeasure is not None for i in result.resultLabInformation.resultDetectionQuantitationLimit) )
            ):
              violations.append(data_rule_12.strip())

      data_rule_13 = """
        CharacteristicName and ResultStatusIdentifier must be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          for result in activity.result:
            if (
              ( result.resultDescription.characteristicName is None ) or
              ( result.resultDescription.resultStatusIdentifier is None )
            ):
              violations.append(data_rule_13.strip())

      data_rule_14 = """
        When DetectionQuantitationLimit's MeasureValue is reported, DetectionQuantitationLimit's MeasureUnitCode must
        be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultLabInformation is not None ) and
                ( result.resultLabInformation.resultDetectionQuantitationLimit is not None )
              ):
                for result_detection_quantitation_limit in result.resultLabInformation.resultDetectionQuantitationLimit:
                  if (
                    ( result_detection_quantitation_limit.detectionQuantitationLimitMeasure is not None ) and
                    ( result_detection_quantitation_limit.detectionQuantitationLimitMeasure.measureValue is not None ) and
                    ( result_detection_quantitation_limit.detectionQuantitationLimitMeasure.measureUnitCode is None )
                  ):
                    violations.append(data_rule_14.strip())

      data_rule_15 = """
        ActivityDescription’s MonitoringLocationIdentifier may be required depending on the value provided for
        ActivityTypeCode. See the domain value list for ActivityTypeCode for more information.
        """
      data_rule_15_domain = []
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.activityDescription is not None ) and
            ( activity.activityDescription.monitoringLocationIdentifier is None ) and
            ( activity.activityDescription.activityTypeCode in data_rule_15_domain )
          ):
            violations.append(data_rule_15.strip())

      data_rule_16 = """
        ResultAnalyticalMethod may be required depending on the value provided for ActivityTypeCode. See the domain
        value list for ActivityTypeCode for more information.
        a. However, ResultAnalyticalMethod is never required if BiologicalIntentName is "Individual", "Population
        Census", "Frequency Class", or "Group Summary"
        """
      data_rule_16_pattern = ['Individual', 'Population Census', 'Frequency Class', 'Group Summary']
      data_rule_16_domain = [] # TODO: Add domain values
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.biologicalResultDescription is not None ) and
                ( result.biologicalResultDescription.biologicalIntentName is not None ) and
                ( not result.biologicalResultDescription.biologicalIntentName in data_rule_16_pattern ) and
                ( result.resultAnalyticalMethod is None ) and
                ( activity.activityDescription is not None ) and
                ( activity.activityDescription.activityTypeCode is not None ) and
                ( activity.activityDescription.activityTypeCode in data_rule_16_domain )
              ):
                violations.append(data_rule_16.strip())

      data_rule_17 = """
        ResultSampleFractionText may be required depending on the value provided for CharacteristicName. See the
        domain value list for CharacteristicName for more information.
        """
      data_rule_17_domain = [] # TODO: Add domain values
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultDescription is not None ) and
                ( result.resultDescription.resultSampleFractionText is None ) and
                ( result.resultDescription.characteristicName is not None ) and
                ( result.resultDescription.characteristicName in data_rule_17_domain )
              ):
                violations.append(data_rule_17.strip())

      data_rule_18 = """
        ResultAnalyticalMethod’s MethodIdentifierContext must either match a value from the AnalyticalMethodContext
        domain list or it must be the same as the value for the OrganizationIdentifier provided in the submission file.
        a. If the MethodIdentifierContext matches a value from the domain list, then the MethodIdentifier must also
        match a value from the AnalyticalMethod domain list (for that Context). Furthermore, MethodName,
        MethodQualifierTypeName, and MethodDescriptionText are not required and will be ignored (since only the
        Identifier and IdentifierContext are needed to uniquely identify the Analytical Method).
        b. If the MethodIdentifierContext matches your OrganizationIdentifier (indicating your own method), then
        MethodIdentifier and MethodName are both required, but do not need to match a value from the domain list
        (since they are your own). Additionally, MethodQualifierTypeName and MethodDescriptionText can be
        provided, but are optional, to further describe the Analytical Method used."
        """
      data_rule_18_domain = []
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultAnalyticalMethod is not None ) and
                ( payload.wqx.organization.organizationDescription is not None ) and
                ( result.resultAnalyticalMethod.methodIdentifierContext != payload.wqx.organization.organizationDescription.organizationIdentifier ) and
                ( not result.resultAnalyticalMethod.methodIdentifierContext in data_rule_18_domain )
              ):
                violations.append(data_rule_18.strip())

      data_rule_19 = """
        ProjectIdentifier, MonitoringLocationIdentifier, ActivityIdentifier, IndexIdentifier and ActivityGroupIdentifier must be
        unique within an Organization. The value for each of these identifiers may occur only once in a submission file.
        a. Unique identifiers are treated as case-insensitive by WQX. For example, the following three identifiers would
        be treated as identical: “Mx571”, “mx571”, “MX571”.
        """
      identifiers:List[str] = []
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None )
      ):
        if payload.wqx.organization.project is not None:
          for project in payload.wqx.organization.project:
            if ( project.projectIdentifier is not None ):
              identifiers.append(project.projectIdentifier.lower())
        if payload.wqx.organization.monitoringLocation is not None:
          for monitoring_location in payload.wqx.organization.monitoringLocation:
            if (
              ( monitoring_location.monitoringLocationIdentity is not None ) and
              ( monitoring_location.monitoringLocationIdentity.monitoringLocationIdentifier is not None )
            ):
              identifiers.append(monitoring_location.monitoringLocationIdentity.monitoringLocationIdentifier.lower())
        if payload.wqx.organization.biologicalHabitatIndex is not None:
          for biological_habitat_index in payload.wqx.organization.biologicalHabitatIndex:
            if biological_habitat_index.indexIdentifier is not None:
              identifiers.append(biological_habitat_index.indexIdentifier.lower())
        if payload.wqx.organization.activity is not None:
          for activity in payload.wqx.organization.activity:
            if (
              ( activity.activityDescription is not None ) and
              ( activity.activityDescription.activityIdentifier is not None )
            ):
              identifiers.append(activity.activityDescription.activityIdentifier.lower())
            if activity.activityMetric is not None:
              for activity_metric in activity.activityMetric:
                if activity_metric.indexIdentifier is not None:
                  identifiers.append(activity_metric.indexIdentifier.lower())
        if payload.wqx.organization.activityGroup is not None:
          for activity_group in payload.wqx.organization.activityGroup:
            if activity_group.activityGroupIdentifier is not None:
              identifiers.append(activity_group.activityGroupIdentifier.lower())
      duplicates:List[str] = [i for i, cnt, in Counter(identifiers).items() if cnt > 1]
      if len(duplicates) > 1:
        violations.append(data_rule_19.strip())

      data_rule_20 = """
        """

      data_rule_21 = """
        ResultMeasure's ResultMeasureValue may be constrained to a list of domain values depending on the value
        provided for CharacteristicName. See the domain value list for CharacteristicName for more information.
        """
      data_rule_21_trigger = []
      data_rule_21_domain = []
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultDescription is not None ) and
                ( result.resultDescription.characteristicName in data_rule_21_trigger ) and
                ( result.resultDescription.resultMeasure.resultMeasureValue not in data_rule_21_domain )
              ):
                violations.append(data_rule_21.strip())

      data_rule_22 = """
        If a numeric value is reported for ResultMeasureValue, then ResultMeasure's MeasureUnitCode and
        ResultValueTypeName are required.
        a. The exception to this is when the ResultMeasureValue is a Characteristic Pick List Value. These do not
        have units.
        """
      data_rule_22_exceptions = []
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultDescription is not None ) and
                ( result.resultDescription.resultMeasure is not None ) and
                ( result.resultDescription.resultMeasure.resultMeasureValue is not None ) and
                ( result.resultDescription.resultMeasure.resultMeasureValue not in data_rule_22_exceptions ) and
                ( result.resultDescription.resultMeasure.resultMeasureValue.isnumeric() ) and
                (
                  ( result.resultDescription.resultMeasure.measureUnitCode is None ) or
                  ( result.resultDescription.resultValueTypeName is None )
                )
              ):
                violations.append(data_rule_22.strip())

      data_rule_23 = """
        If a CountyCode is reported then a StateCode must also be reported.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.monitoringLocation is not None )
      ):
        if payload.wqx.organization.monitoringLocation is not None:
          for monitoring_location in payload.wqx.organization.monitoringLocation:
            if (
              ( monitoring_location.monitoringLocationGeospatial is not None ) and
              ( monitoring_location.monitoringLocationGeospatial.countyCode is not None ) and
              ( monitoring_location.monitoringLocationGeospatial.stateCode is None )
            ):
              violations.append(data_rule_23.strip())
        if payload.wqx.organization.organizationAddress is not None:
          for organization_address in payload.wqx.organization.organizationAddress:
            if (
              ( organization_address.countyCode is not None ) and
              ( organization_address.stateCode is None )
            ):
              violations.append(data_rule_23.strip())

      data_rule_24 = """
        If NetTypeName = "Net/Horizontal Tow" then BoatSpeedMeasure is required.
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.biologicalActivityDescription is not None ) and
            ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation is not None ) and
            ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation is not None ) and
            ( 'Net/Horizontal Tow' == activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netTypeName ) and
            ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.boatSpeedMeasure is None )
          ):
            violations.append(data_rule_24.strip())

      data_rule_25 = """
        If NetTypeName is reported then the SampleCollectionEquipmentName must be one that relates to that type of
        equipment.
        """
      # TODO: Figure out how to report violations of this rule

      data_rule_26 = """
        ActivityMetric's MetricTypeIdentifierContext must either match a value from the MetricTypeContext domain list or it
        must be the same as the value for the OrganizationIdentifier provided in the submission file.
        a. If the MetricTypeIdentifierContext matches a value from the domain list, then the MetricTypeIdentifier must
        also match a value from the MetricType domain list (for that Context). Furthermore, MetricTypeName,
        MetricTypeCitation, MetricTypeScaleText, and FormulaDescriptionText are not required and will be ignored
        (since only the Identifier and IdentifierContext are needed to uniquely identify the MetricType).
        b. If the MetricTypeIdentifierContext matches your OrganizationIdentifier (indicating your own metric), then
        MetricTypeIdentifier and MetricTypeName are both required, but do not need to match a value from the
        domain list (since they are your own). Additionally, MetricTypeCitation, MetricTypeScaleText, and
        FormulaDescriptionText can be provided, but are optional, to further describe the Metric Type used.
        """
      data_rule_26_metric_type_context_domain = []
      data_rule_26_metric_type_domain = []
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.activityMetric is not None:
            for activity_metric in activity.activityMetric:
              if activity_metric.activityMetricType is not None:
                if activity_metric.activityMetricType.metricTypeIdentifierContext == payload.wqx.organization.organizationDescription.organizationIdentifier:
                  if (
                    ( activity_metric.activityMetricType.metricTypeIdentifier is None ) or
                    ( activity_metric.activityMetricType.metricTypeName is None )
                  ):
                    violations.append(data_rule_26.strip())
                elif activity_metric.activityMetricType.metricTypeIdentifierContext in data_rule_26_metric_type_context_domain:
                  if activity_metric.activityMetricType.metricTypeIdentifier not in data_rule_26_metric_type_domain:
                    violations.append(data_rule_26.strip())
                else:
                  violations.append(data_rule_26.strip())

      data_rule_27 = """
        If BiologicalIntentName is "Group Summary" then GroupSummaryCount or GroupSummaryWeight must be reported
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.biologicalResultDescription is not None ) and
                ( 'Group Summary' == result.biologicalResultDescription.biologicalIntentName ) and
                (
                  ( result.biologicalResultDescription.groupSummaryCount is None ) or
                  ( result.biologicalResultDescription.groupSummaryWeightMeasure is None )
                )
              ):
                violations.append(data_rule_27.strip())

      data_rule_28 = """
        If BiologicalIntentName is "Frequency Class" then Result's CharacteristicName must be "Count"
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.biologicalResultDescription is not None ) and
                ( 'Frequency Class' == result.biologicalResultDescription.biologicalIntentName ) and
                ( 'Count' != result.resultDescription.characteristicName )
              ):
                violations.append(data_rule_28.strip())

      data_rule_29 = """
        If BiologicalIntentName is "Population Census" then Result's CharacteristicName must be "Count" or "Total Sample
        Weight"
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.biologicalResultDescription is not None ) and
                ( 'Population Census' == result.biologicalResultDescription.biologicalIntentName ) and
                (
                  ( result.resultDescription is None ) or
                  ( result.resultDescription.characteristicName is None ) or
                  ( result.resultDescription.characteristicName not in ['Count', 'Total Sample Weight'])
                )
              ):
                violations.append(data_rule_29.strip())

      data_rule_30 = """
        FrequencyClassDescriptorUnitCode may be required depending on the value provided for
        FrequencyClassDescriptorCode. See the domain value list for FrequencyClassType for more information.
        """
      data_rule_30_domain = []
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.biologicalResultDescription is not None ) and
                ( result.biologicalResultDescription.frequencyClassInformation is not None )
              ):
                for frequency_class_information in result.biologicalResultDescription.frequencyClassInformation:
                  if (
                    ( frequency_class_information.frequencyClassDescriptorUnitCode is None ) and
                    ( frequency_class_information.frequencyClassDescriptorCode is not None ) and
                    ( frequency_class_information.frequencyClassDescriptorCode in data_rule_30_domain )
                  ):
                    violations.append(data_rule_30.strip())

      data_rule_31 = """
        FrequencyClassInformation's LowerClassBoundValue and UpperClassBoundValue may be required depending on
        the value provided for FrequencyClassDescriptorCode. See the domain value list for FrequencyClassType for more
        information
        """
      data_rule_31_domain = []
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.biologicalResultDescription is not None ) and
                ( result.biologicalResultDescription.frequencyClassInformation is not None )
              ):
                for frequency_class_information in result.biologicalResultDescription.frequencyClassInformation:
                  if (
                    (
                      ( frequency_class_information.lowerClassBoundValue is None ) or
                      ( frequency_class_information.upperClassBoundValue is None )
                    ) and
                    ( frequency_class_information.frequencyClassDescriptorCode is not None ) and
                    ( frequency_class_information.frequencyClassDescriptorCode in data_rule_31_domain )
                  ):
                    violations.append(data_rule_31.strip())

      data_rule_32 = """
        Biological Intent Name and Subject Taxonomic Name must be reported when Activity Media Name is "Biological" or
        "Tissue"
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.activityDescription is not None ) and
            ( activity.activityDescription.activityMediaName is not None ) and
            ( activity.activityDescription.activityMediaName in ['Biological', 'Tissue'] )
          ):
            for result in activity.result:
              if (
                ( result.biologicalResultDescription is None ) or
                ( result.biologicalResultDescription.biologicalIntentName is None ) or
                ( result.biologicalResultDescription.subjectTaxonomicName is None )
              ):
                violations.append(data_rule_32.strip())

      data_rule_33 = """
        Either Result Measure Value and/or Result Detection Condition Text must be reported
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultDescription is None ) or
                ( result.resultDescription.resultMeasure is None ) or
                (
                  ( result.resultDescription.resultMeasure.resultMeasureValue is None ) and
                  ( result.resultDescription.resultDetectionConditionText is None )
                )
              ):
                violations.append(data_rule_33.strip())

      data_rule_34 = """
        Habitat Selection Method is required when Activity Assemblage is "Benthic Macroinvertebrates"
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.biologicalActivityDescription is not None ) and
            ( activity.biologicalActivityDescription.assemblageSampledName is not None ) and
            ( 'Benthic Macroinvertebrates' == activity.biologicalActivityDescription.assemblageSampledName ) and
            (
              ( activity.biologicalActivityDescription is None ) or
              ( activity.biologicalActivityDescription.habitatSelectionMethod is None )
            )
          ):
            violations.append(data_rule_34.strip())

      data_rule_35 = """
        Measure Unit is required when Measure Value is supplied
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None )
      ):
        if payload.wqx.organization.activity is not None:
          for activity in payload.wqx.organization.activity:
            if activity.result is not None:
              for result in activity.result:
                if (
                  (
                    ( result.resultDescription is not None ) and
                    ( result.resultDescription.resultMeasure is not None ) and
                    ( result.resultDescription.resultMeasure.resultMeasureValue is not None ) and
                    ( result.resultDescription.resultMeasure.measureUnitCode is None )
                  ) or (
                    ( result.resultDescription is not None ) and
                    ( result.resultDescription.resultDepthHeightMeasure is not None ) and
                    ( result.resultDescription.resultDepthHeightMeasure.measureValue is not None ) and
                    ( result.resultDescription.resultDepthHeightMeasure.measureUnitCode is None )
                  )
                ):
                  violations.append(data_rule_35.strip())
            if (
              (
                ( activity.activityDescription is not None ) and
                (
                  (
                    ( activity.activityDescription.activityDepthHeightMeasure is not None ) and
                    ( activity.activityDescription.activityDepthHeightMeasure.measureValue is not None ) and
                    ( activity.activityDescription.activityDepthHeightMeasure.measureUnitCode is None )
                  ) or (
                    ( activity.activityDescription.activityTopDepthHeightMeasure is not None ) and
                    ( activity.activityDescription.activityTopDepthHeightMeasure.measureValue is not None ) and
                    ( activity.activityDescription.activityTopDepthHeightMeasure.measureUnitCode is None )
                  ) or (
                    ( activity.activityDescription.activityBottomDepthHeightMeasure is not None ) and
                    ( activity.activityDescription.activityBottomDepthHeightMeasure.measureValue is not None ) and
                    ( activity.activityDescription.activityBottomDepthHeightMeasure.measureUnitCode is None )
                  )
                )
              ) or (
                ( activity.activityLocation is not None ) and
                ( activity.activityLocation.horizontalAccuracyMeasure is not None ) and
                ( activity.activityLocation.horizontalAccuracyMeasure.measureValue is not None ) and
                ( activity.activityLocation.horizontalAccuracyMeasure.measureUnitCode is None )
              ) or (
                ( activity.biologicalActivityDescription is not None ) and
                ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation is not None ) and
                (
                  (
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionDuration is not None ) and
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionDuration.measureValue is not None ) and
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionDuration.measureUnitCode is None )
                  ) or (
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionArea is not None ) and
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionArea.measureValue is not None ) and
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionArea.measureUnitCode is None )
                  ) or (
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachLengthMeasure is not None ) and
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachLengthMeasure.measureValue is not None ) and
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachLengthMeasure.measureUnitCode is None )
                  ) or (
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachWidthMeasure is not None ) and
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachWidthMeasure.measureValue is not None ) and
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachWidthMeasure.measureUnitCode is None )
                  ) or (
                    ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation is not None ) and
                    (
                      (
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netSurfaceAreaMeasure is not None ) and
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netSurfaceAreaMeasure.measureValue is not None ) and
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netSurfaceAreaMeasure.measureUnitCode is None )
                      ) or (
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netMeshSizeMeasure is not None ) and
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netMeshSizeMeasure.measureValue is not None ) and
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netMeshSizeMeasure.measureUnitCode is None )
                      ) or (
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.boatSpeedMeasure is not None ) and
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.boatSpeedMeasure.measureValue is not None ) and
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.boatSpeedMeasure.measureUnitCode is None )
                      ) or (
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.currentSpeedMeasure is not None ) and
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.currentSpeedMeasure.measureValue is not None ) and
                        ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.currentSpeedMeasure.measureUnitCode is None )
                      )
                    )
                  )
                )
              )
            ):
              violations.append(data_rule_35.strip())
            if activity.activityMetric is not None:
              for activity_metric in activity.activityMetric:
                if (
                  ( activity_metric.metricValueMeasure is not None ) and
                  ( activity_metric.metricValueMeasure.measureValue is not None ) and
                  ( activity_metric.metricValueMeasure.measureUnitCode is None )
                ):
                  violations.append(data_rule_35.strip())
            if activity.result is not None:
              for result in activity.result:
                if (
                  ( result.resultLabInformation is not None ) and
                  ( result.resultLabInformation.resultDetectionQuantitationLimit is not None )
                ):
                  for detection_quantitation_limit in result.resultLabInformation.resultDetectionQuantitationLimit:
                    if (
                      ( detection_quantitation_limit.detectionQuantitationLimitMeasure is not None ) and
                      ( detection_quantitation_limit.detectionQuantitationLimitMeasure.measureValue is not None ) and
                      ( detection_quantitation_limit.detectionQuantitationLimitMeasure.measureUnitCode is None )
                    ):
                      violations.append(data_rule_35.strip())
                if (
                  ( result.biologicalResultDescription is not None ) and
                  ( result.biologicalResultDescription.groupSummaryWeightMeasure is not None ) and
                  ( result.biologicalResultDescription.groupSummaryWeightMeasure.measureValue is not None ) and
                  ( result.biologicalResultDescription.groupSummaryWeightMeasure.measureUnitCode is None )
                ):
                  violations.append(data_rule_35.strip())
        if payload.wqx.organization.monitoringLocation is not None:
          for monitoring_location in payload.wqx.organization.monitoringLocation:
            if (
              (
                ( monitoring_location.monitoringLocationGeospatial is not None ) and
                (
                  (
                    ( monitoring_location.monitoringLocationGeospatial.horizontalAccuracyMeasure is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.horizontalAccuracyMeasure.measureValue is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.horizontalAccuracyMeasure.measureUnitCode is None )
                  ) or (
                    ( monitoring_location.monitoringLocationGeospatial.verticalAccuracyMeasure is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.verticalAccuracyMeasure.measureValue is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.verticalAccuracyMeasure.measureUnitCode is None )
                  ) or (
                    ( monitoring_location.monitoringLocationGeospatial.verticalMeasure is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.verticalMeasure.measureValue is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.verticalMeasure.measureUnitCode is None )
                  )
                )
              ) or (
                ( monitoring_location.monitoringLocationIdentity is not None ) and
                (
                  (
                    ( monitoring_location.monitoringLocationIdentity.drainageAreaMeasure is not None ) and
                    ( monitoring_location.monitoringLocationIdentity.drainageAreaMeasure.measureValue is not None ) and
                    ( monitoring_location.monitoringLocationIdentity.drainageAreaMeasure.measureUnitCode is None )
                  ) or (
                    ( monitoring_location.monitoringLocationIdentity.contributingDrainageAreaMeasure is not None ) and
                    ( monitoring_location.monitoringLocationIdentity.contributingDrainageAreaMeasure.measureValue is not None ) and
                    ( monitoring_location.monitoringLocationIdentity.contributingDrainageAreaMeasure.measureUnitCode is None )
                  )
                )
              ) or (
                ( monitoring_location.wellInformation is not None ) and
                (
                  (
                    ( monitoring_location.wellInformation.wellHoleDepthMeasure is not None ) and
                    ( monitoring_location.wellInformation.wellHoleDepthMeasure.measureValue is not None ) and
                    ( monitoring_location.wellInformation.wellHoleDepthMeasure.measureUnitCode is None )
                  ) or (
                    ( monitoring_location.wellInformation.wellDepthMeasure is not None ) and
                    ( monitoring_location.wellInformation.wellDepthMeasure.measureValue is not None ) and
                    ( monitoring_location.wellInformation.wellDepthMeasure.measureUnitCode is None )
                  )
                )
              )
            ):
              violations.append(data_rule_35.strip())
        if payload.wqx.organization.project is not None:
          for project in payload.wqx.organization.project:
            for project_monitoring_location_weighting in project.projectMonitoringLocationWeighting:
              if (
                ( project_monitoring_location_weighting.locationWeightingFactorMeasure is not None ) and
                ( project_monitoring_location_weighting.locationWeightingFactorMeasure.measureValue is not None ) and
                ( project_monitoring_location_weighting.locationWeightingFactorMeasure.measureUnitCode is None )
              ):
                violations.append(data_rule_35.strip())

      data_rule_36 = """
        Measure Value is required when Measurement Unit is supplied
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                (
                  ( result.resultDescription is not None ) and
                  ( result.resultDescription.resultMeasure is not None ) and
                  ( result.resultDescription.resultMeasure.resultMeasureValue is None ) and
                  ( result.resultDescription.resultMeasure.measureUnitCode is not None )
                ) or (
                  ( result.resultDescription is not None ) and
                  ( result.resultDescription.resultDepthHeightMeasure is not None ) and
                  ( result.resultDescription.resultDepthHeightMeasure.measureValue is None ) and
                  ( result.resultDescription.resultDepthHeightMeasure.measureUnitCode is not None )
                )
              ):
                violations.append(data_rule_36.strip())
          if (
            (
              ( activity.activityDescription is not None ) and
              (
                (
                  ( activity.activityDescription.activityDepthHeightMeasure is not None ) and
                  ( activity.activityDescription.activityDepthHeightMeasure.measureValue is None ) and
                  ( activity.activityDescription.activityDepthHeightMeasure.measureUnitCode is not None )
                ) or (
                  ( activity.activityDescription.activityTopDepthHeightMeasure is not None ) and
                  ( activity.activityDescription.activityTopDepthHeightMeasure.measureValue is None ) and
                  ( activity.activityDescription.activityTopDepthHeightMeasure.measureUnitCode is not None )
                ) or (
                  ( activity.activityDescription.activityBottomDepthHeightMeasure is not None ) and
                  ( activity.activityDescription.activityBottomDepthHeightMeasure.measureValue is None ) and
                  ( activity.activityDescription.activityBottomDepthHeightMeasure.measureUnitCode is not None )
                )
              )
            ) or (
              ( activity.activityLocation is not None ) and
              ( activity.activityLocation.horizontalAccuracyMeasure is not None ) and
              ( activity.activityLocation.horizontalAccuracyMeasure.measureValue is None ) and
              ( activity.activityLocation.horizontalAccuracyMeasure.measureUnitCode is not None )
            ) or (
              ( activity.biologicalActivityDescription is not None ) and
              ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation is not None ) and
              (
                (
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionDuration is not None ) and
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionDuration.measureValue is None ) and
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionDuration.measureUnitCode is not None )
                ) or (
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionArea is not None ) and
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionArea.measureValue is None ) and
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.collectionArea.measureUnitCode is not None )
                ) or (
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachLengthMeasure is not None ) and
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachLengthMeasure.measureValue is None ) and
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachLengthMeasure.measureUnitCode is not None )
                ) or (
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachWidthMeasure is not None ) and
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachWidthMeasure.measureValue is None ) and
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.reachWidthMeasure.measureUnitCode is not None )
                ) or (
                  ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation is not None ) and
                  (
                    (
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netSurfaceAreaMeasure is not None ) and
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netSurfaceAreaMeasure.measureValue is None ) and
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netSurfaceAreaMeasure.measureUnitCode is not None )
                    ) or (
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netMeshSizeMeasure is not None ) and
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netMeshSizeMeasure.measureValue is None ) and
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.netMeshSizeMeasure.measureUnitCode is not None )
                    ) or (
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.boatSpeedMeasure is not None ) and
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.boatSpeedMeasure.measureValue is None ) and
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.boatSpeedMeasure.measureUnitCode is not None )
                    ) or (
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.currentSpeedMeasure is not None ) and
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.currentSpeedMeasure.measureValue is None ) and
                      ( activity.biologicalActivityDescription.biologicalHabitatCollectionInformation.netInformation.currentSpeedMeasure.measureUnitCode is not None )
                    )
                  )
                )
              )
            )
          ):
            violations.append(data_rule_36.strip())
          if activity.activityMetric is not None:
            for activity_metric in activity.activityMetric:
              if (
                ( activity_metric.metricValueMeasure is not None ) and
                ( activity_metric.metricValueMeasure.measureValue is None ) and
                ( activity_metric.metricValueMeasure.measureUnitCode is not None )
              ):
                violations.append(data_rule_36.strip())
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultLabInformation is not None ) and
                ( result.resultLabInformation.resultDetectionQuantitationLimit is not None )
              ):
                for detection_quantitation_limit in result.resultLabInformation.resultDetectionQuantitationLimit:
                  if (
                    ( detection_quantitation_limit.detectionQuantitationLimitMeasure is not None ) and
                    ( detection_quantitation_limit.detectionQuantitationLimitMeasure.measureValue is None ) and
                    ( detection_quantitation_limit.detectionQuantitationLimitMeasure.measureUnitCode is not None )
                  ):
                    violations.append(data_rule_36.strip())
              if (
                (
                  ( result.biologicalResultDescription is not None ) and
                  ( result.biologicalResultDescription.groupSummaryWeightMeasure is not None ) and
                  ( result.biologicalResultDescription.groupSummaryWeightMeasure.measureValue is None ) and
                  ( result.biologicalResultDescription.groupSummaryWeightMeasure.measureUnitCode is not None )
                )
              ):
                violations.append(data_rule_36.strip())
        if payload.wqx.organization.monitoringLocation is not None:
          for monitoring_location in payload.wqx.organization.monitoringLocation:
            if (
              (
                ( monitoring_location.monitoringLocationGeospatial is not None ) and
                (
                  (
                    ( monitoring_location.monitoringLocationGeospatial.horizontalAccuracyMeasure is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.horizontalAccuracyMeasure.measureValue is None ) and
                    ( monitoring_location.monitoringLocationGeospatial.horizontalAccuracyMeasure.measureUnitCode is not None )
                  ) or (
                    ( monitoring_location.monitoringLocationGeospatial.verticalAccuracyMeasure is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.verticalAccuracyMeasure.measureValue is None ) and
                    ( monitoring_location.monitoringLocationGeospatial.verticalAccuracyMeasure.measureUnitCode is not None )
                  ) or (
                    ( monitoring_location.monitoringLocationGeospatial.verticalMeasure is not None ) and
                    ( monitoring_location.monitoringLocationGeospatial.verticalMeasure.measureValue is None ) and
                    ( monitoring_location.monitoringLocationGeospatial.verticalMeasure.measureUnitCode is not None )
                  )
                )
              ) or (
                ( monitoring_location.monitoringLocationIdentity is not None ) and
                (
                  (
                    ( monitoring_location.monitoringLocationIdentity.drainageAreaMeasure is not None ) and
                    ( monitoring_location.monitoringLocationIdentity.drainageAreaMeasure.measureValue is None ) and
                    ( monitoring_location.monitoringLocationIdentity.drainageAreaMeasure.measureUnitCode is not None )
                  ) or (
                    ( monitoring_location.monitoringLocationIdentity.contributingDrainageAreaMeasure is not None ) and
                    ( monitoring_location.monitoringLocationIdentity.contributingDrainageAreaMeasure.measureValue is None ) and
                    ( monitoring_location.monitoringLocationIdentity.contributingDrainageAreaMeasure.measureUnitCode is not None )
                  )
                )
              ) or (
                ( monitoring_location.wellInformation is not None ) and
                (
                  (
                    ( monitoring_location.wellInformation.wellHoleDepthMeasure is not None ) and
                    ( monitoring_location.wellInformation.wellHoleDepthMeasure.measureValue is None ) and
                    ( monitoring_location.wellInformation.wellHoleDepthMeasure.measureUnitCode is not None )
                  ) or (
                    ( monitoring_location.wellInformation.wellDepthMeasure is not None ) and
                    ( monitoring_location.wellInformation.wellDepthMeasure.measureValue is None ) and
                    ( monitoring_location.wellInformation.wellDepthMeasure.measureUnitCode is not None )
                  )
                )
              )
            ):
              violations.append(data_rule_35.strip())
        if payload.wqx.organization.project is not None:
          for project in payload.wqx.organization.project:
            if project.projectMonitoringLocationWeighting is not None:
              for project_monitoring_location_weighting in project.projectMonitoringLocationWeighting:
                if (
                  ( project_monitoring_location_weighting.locationWeightingFactorMeasure is not None ) and
                  ( project_monitoring_location_weighting.locationWeightingFactorMeasure.measureValue is None ) and
                  ( project_monitoring_location_weighting.locationWeightingFactorMeasure.measureUnitCode is not None )
                ):
                  violations.append(data_rule_36.strip())

      data_rule_37 = """
        Target Count is required when the Activity Assemblage is "Benthic Macroinvertebrates"
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.biologicalActivityDescription is not None ) and
            ( 'Benthic Macroinvertebrates' == activity.biologicalActivityDescription.assemblageSampledName ) and
            ( activity.result is not None )
          ):
            for result in activity.result:
              if (
                ( result.resultDescription is None ) or
                ( result.resultDescription.targetCount is None )
              ):
                violations.append(data_rule_37.strip())

      data_rule_38 = """
        Percent Sample Processed Numeric is required when the Activity Assemblage is "Benthic Macroinvertebrates"
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if (
            ( activity.biologicalActivityDescription is not None ) and
            ( 'Benthic Macroinvertebrates' == activity.biologicalActivityDescription.assemblageSampledName ) and
            ( activity.result is not None )
          ):
            for result in activity.result:
              if (
                ( result.resultDescription is None ) or
                ( result.resultDescription.proportionSampleProcessedNumeric is None )
              ):
                violations.append(data_rule_38.strip())

      data_rule_39 = """
        Percent Sample Processed Numeric must be a positive number between 0 and 1"
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultDescription is not None ) and
                ( result.resultDescription.proportionSampleProcessedNumeric is not None ) and
                (
                  ( result.resultDescription.proportionSampleProcessedNumeric < 0 ) or
                  ( result.resultDescription.proportionSampleProcessedNumeric > 1 )
                )
              ):
                violations.append(data_rule_39.strip())

      data_rule_40 = """
        Removed (v3.0) Sample Collection Method is required when Activity Type Code contains the word "Sample"
        """
      # Not enforced because rule indicates it was removed.

      data_rule_41 = """
        Statistical N-Value Numeric must be a positive whole number
        """
      if (
        ( payload.wqx is not None ) and
        ( payload.wqx.organization is not None ) and
        ( payload.wqx.organization.activity is not None )
      ):
        for activity in payload.wqx.organization.activity:
          if activity.result is not None:
            for result in activity.result:
              if (
                ( result.resultDescription is not None ) and
                ( result.resultDescription.statisticalNValueNumeric is not None ) and
                ( result.resultDescription.statisticalNValueNumeric < 0 )
              ):
                violations.append(data_rule_41.strip())

    return violations

  def list_rule_violations(self) -> List[str]:
    violations:List[str] = []
    
    violations.extend(self.list_data_rule_violations())
    violations.extend(self.list_xsd_rule_violations())

    return violations

  def list_xsd_rule_violations(self) -> List[str]:
    """This function is not yet implemented. XSD rule violations will cause
    generateXML to raise a WQXException, which should be handled when called."""
    violations:List[str] = []
    
    return violations

  def generateXML(self, name:str = 'Document') -> str:
    doc, tag, text, line = Doc().ttl()

    violations = self.list_rule_violations()

    if len(violations) > 0:
      raise WQXException(f"The document contains {len(violations)} data rule violations. Use list_rule_violations function for list.")

    if self.__id is None:
      raise WQXException("Attribute 'id' is required.")
    doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
    with tag(name,
      ('Id', self.__id),
      ('xmlns','http://www.exchangenetwork.net/schema/v1.0/ExchangeNetworkDocument.xsd'),
      ('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    ):
      if self.__header is None:
        raise WQXException("Attribute 'header' is required.")
      doc.asis(self.__header.generateXML('Header'))
      if len(self.__payload) < 1:
        raise WQXException("Attribute 'payload' must be a list of 1 or more Payload objects.")
      for x in self.__payload:
        doc.asis(x.generateXML('Payload'))

    return indent(doc.getvalue(), indentation=' '*2)
