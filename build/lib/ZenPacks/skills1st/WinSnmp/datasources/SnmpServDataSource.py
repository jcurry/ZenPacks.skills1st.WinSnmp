from zope.component import adapts
from zope.interface import implements
 
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t
 
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSource, PythonDataSourcePlugin

from pynetsnmp.twistedsnmp import AgentProxy

# Setup logging
import logging
log = logging.getLogger('zen.PythonWinSnmp')

svSvcNumber = '.1.3.6.1.4.1.77.1.2.2.0'

def getSnmpV3Args(ds0):
    snmpv3Args = []
    if '3' in ds0.zSnmpVer:
        if ds0.zSnmpPrivType:
            snmpv3Args += ['-l', 'authPriv']
            snmpv3Args += ['-x', ds0.zSnmpPrivType]
            snmpv3Args += ['-X', ds0.zSnmpPrivPassword]
        elif ds0.zSnmpAuthType:
            snmpv3Args += ['-l', 'authNoPriv']
        else:
            snmpv3Args += ['-l', 'noAuthNoPriv']
        if ds0.zSnmpAuthType:
            snmpv3Args += ['-a', ds0.zSnmpAuthType]
            snmpv3Args += ['-A', ds0.zSnmpAuthPassword]
            snmpv3Args += ['-u', ds0.zSnmpSecurityName]
    return snmpv3Args

def get_snmp_proxy(ds0, config):
    snmpV3Args = getSnmpV3Args(ds0)
    log.debug( 'snmpV3Args are %s ' % (snmpV3Args))
    snmp_proxy = AgentProxy(
        ip = ds0.manageIp,
        port=int(ds0.zSnmpPort),
        timeout=ds0.zSnmpTimeout,
        snmpVersion=ds0.zSnmpVer,
        community=ds0.zSnmpCommunity,
        cmdLineArgs=snmpV3Args,
        protocol=None,
        allowCache=False
        )
    snmp_proxy.open()
    return snmp_proxy


def getScalarStuff(snmp_proxy, scalarOIDstrings):
    # scalarOIDstring must be a list
    # NB scalarOIDstrings MUST all come from the same SNMP table or you get no data returned
    # NB Windows net-snmp agent 5.5.0-1 return null dictionary if
    #     input list is > 1 oid - maybe ?????
    # Agent Proxy get returns dict of {oid_str : <value>}
    log.debug('In getScalarStuff - snmp_proxy is %s and scalarOIDstrings is %s \n' % (snmp_proxy, scalarOIDstrings))
    d=snmp_proxy.get(scalarOIDstrings)
    return d

def getTableStuff(snmp_proxy, OIDstrings):
    d=snmp_proxy.getTable(OIDstrings)
    return d


class SnmpServDataSource(PythonDataSource):
    """ Get  number of services
        for Windows devices using SNMP """
 
    ZENPACKID = 'ZenPacks.skills1st.WinSnmp'
 
    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('SnmpServDataSource',)
    sourcetype = sourcetypes[0]
 
    component = '${here/id}'
    eventClass = '/Perf/Snmp'

    # Custom fields in the datasource - with default values
    #    (which can be overriden in template )
    hostname = '${dev/id}'
    ipAddress = '${dev/manageIp}'
    snmpVer = '${dev/zSnmpVer}'
    snmpCommunity = '${dev/zSnmpCommunity}'
    # cycletime is standard and defaults to 300

    cycletime = 300

    _properties = PythonDataSource._properties + (
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'ipAddress', 'type': 'string', 'mode': 'w'},
        {'id': 'snmpVer', 'type': 'string', 'mode': 'w'},
        {'id': 'snmpCommunity', 'type': 'string', 'mode': 'w'},
    )

    # Collection plugin for this type. Defined below in this file.
    plugin_classname = ZENPACKID + '.datasources.SnmpServDataSource.SnmpServPlugin'
    # 
    def addDataPoints(self):
        if not self.datapoints._getOb('svSvcNumber', None):
            self.manage_addRRDDataPoint('svSvcNumber')

class ISnmpServDataSourceInfo(IRRDDataSourceInfo):
    """Interface that creates the web form for this data source type."""
 
    hostname = schema.TextLine(
        title=_t(u'Host Name'),
        group=_t('SnmpServDataSource'))
    ipAddress = schema.TextLine(
        title=_t(u'IP Address'),
        group=_t('SnmpServDataSource'))
    snmpVer = schema.TextLine(
        title=_t(u'SNMP Version'),
        group=_t('SnmpServDataSource'))
    snmpCommunity = schema.TextLine(
        title=_t(u'SNMP Community'),
        group=_t('SnmpServDataSource'))

    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))
 
 
class SnmpServDataSourceInfo(RRDDataSourceInfo):
    """Adapter between ISnmpServDataSourceInfo and SnmpServDataSource."""
 
    implements(ISnmpServDataSourceInfo)
    adapts(SnmpServDataSource)
 
    hostname = ProxyProperty('hostname')
    ipAddress = ProxyProperty('ipAddress')
    snmpVer = ProxyProperty('snmpVer')
    snmpCommunity = ProxyProperty('snmpCommunity')

    cycletime = ProxyProperty('cycletime')

    # Doesn't seem to run in the GUI if you activate the test button
    testable = False
    #testable = True
 
class SnmpServPlugin(PythonDataSourcePlugin):
    """
    Collection plugin class for SnmpServDataSource.
 
    """
    # List of device attributes you might need to do collection.
    proxy_attributes = (
        'zSnmpVer',
        'zSnmpCommunity',
        'zSnmpPort',
        'zSnmpMonitorIgnore',
        'zSnmpAuthPassword',
        'zSnmpAuthType',
        'zSnmpPrivPassword',
        'zSnmpPrivType',
        'zSnmpSecurityName',
        'zSnmpTimeout',
        'zSnmpTries',
        'zMaxOIDPerRequest',
        )

    @classmethod
    def config_key(cls, datasource, context):
        """
        Return a tuple defining collection uniqueness.
 
        This is a classmethod that is executed in zenhub. The datasource and
        context parameters are the full objects.
 
        This example implementation is the default. Split configurations by
        device, cycle time, template id, datasource id and the Python data
        source's plugin class name.
 
        You can omit this method from your implementation entirely if this
        default uniqueness behavior fits your needs. In many cases it will.
        """
        # Logging in this method will be to zenhub.log

        log.debug( 'In config_key context.device().id is %s datasource.getCycleTime(context) is %s datasource.rrdTemplate().id is %s datasource.id is %s datasource.plugin_classname is %s  ' % (context.device().id, datasource.getCycleTime(context), datasource.rrdTemplate().id, datasource.id, datasource.plugin_classname))
        return (
            context.device().id,
            datasource.getCycleTime(context),
            datasource.rrdTemplate().id,
            datasource.id,
            datasource.plugin_classname,
            )
 
    @classmethod
    def params(cls, datasource, context):
        """
        Return params dictionary needed for this plugin.
 
        This is a classmethod that is executed in zenhub. The datasource and
        context parameters are the full objects.

        You have access to the dmd object database here and any attributes
        and methods for the context (either device or component).
 
        You can omit this method from your implementation if you don't require
        any additional information on each of the datasources of the config
        parameter to the collect method below. If you only need extra
        information at the device level it is easier to just use
        proxy_attributes as mentioned above.
        """
        params = {}
        log.debug(' params is %s \n' % (params))
        return params

 
    def collect(self, config):
        """
        No default collect behavior. You must implement this method.
 
        This method must return a Twisted deferred. The deferred results will
        be sent to the onResult then either onSuccess or onError callbacks
        below.

        This method really is run by zenpython daemon. Check zenpython.log
        for any log messages.
        """

        ds0 = config.datasources[0]
        # Open the Snmp AgentProxy connection
        self._snmp_proxy = get_snmp_proxy(ds0, config)

        # NB NB NB - When getting scalars, they must all come from the SAME snmp table

        # Now get data - 1 scalar OIDs
        d=getScalarStuff(self._snmp_proxy, [ svSvcNumber,]) 
        return d

    def onResult(self, result, config):
        """
        Called first for success and error.
 
        You can omit this method if you want the result of the collect method
        to be used without further processing.
        """
        log.debug( 'result is %s ' % (result))

        return result
 
    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
 
        You should return a data structure with zero or more events, values
        and maps.
        Note that values is a dictionary and events and maps are lists.

        return {
            'events': [{
                'summary': 'successful collection',
                'eventKey': 'myPlugin_result',
                'severity': 0,
                },{
                'summary': 'first event summary',
                'eventKey': 'myPlugin_result',
                'severity': 2,
                },{
                'summary': 'second event summary',
                'eventKey': 'myPlugin_result',
                'severity': 3,
                }],
 
            'values': {
                None: {  # datapoints for the device (no component)
                    'datapoint1': 123.4,
                    'datapoint2': 5.678,
                    },
                'cpu1': {
                    'user': 12.1,
                    nsystem': 1.21,
                    'io': 23,
                    }
                },
 
            'maps': [
                ObjectMap(...),
                RelationshipMap(..),
                ]
            }
            """

        log.debug( 'In success - result is %s and config is %s ' % (result, config))
        # Next line creates a dictionary like 
        #          {'values': defaultdict(<type 'dict'>, {}), 'events': [], 'maps':[]}
        # the new_data method is defined in PythonDataSource.py in the Python Collector
        #     ZenPack, datasources directory

        data = self.new_data()

        # Format of result output is a dict with { oid:value } - INCLUDING leading dot !!
        #       svSvcNumber = '.1.3.6.1.4.1.77.1.2.2.0'
        # Remember datapoint name is svSvcNumber
        # This is being kind to users giving them a datapoint that is somewhat meaningful
        # If you want to be cruel, define the datapoint as the OID string and simply return
        #   the results dictionary

        datapointDict = {}
        for k,v in result.iteritems():
            if k == svSvcNumber:
                datapointDict['svSvcNumber'] = v

        log.debug('datapointDict is %s \n ' % (datapointDict))
        data['values'] = {
                None : datapointDict
                }

        # You don't have to provide an event - comment this out if so
        data['events'].append({
                    'device': config.id,
                    'summary': 'service data gathered using zenpython with snmp',
                    'severity': 1,
                    'eventClass': '/App',
                    'eventKey': 'PythonSnmpServ',
                    })

        data['maps'] = []

        log.debug( 'data is %s ' % (data))
        return data

    def onError(self, result, config):
        """
        Called only on error. After onResult, before onComplete.
 
        You can omit this method if you want the error result of the collect
        method to be used without further processing. It recommended to
        implement this method to capture errors.
        """
        log.debug( 'In OnError - result is %s and config is %s ' % (result, config))
        return {
            'events': [{
                'summary': 'Error getting Snmp services data with zenpython: %s' % result,
                'eventKey': 'PythonSnmpServ',
                'severity': 4,
                }],
            }
 
    def onComplete(self, result, config):
        """
        Called last for success and error.
 
        You can omit this method if you want the result of either the
        onSuccess or onError method to be used without further processing.
        """
        self._snmp_proxy.close()
        return result

