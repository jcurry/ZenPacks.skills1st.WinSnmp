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
from Products.ZenUtils.Utils import prepId


# Setup logging
import logging
log = logging.getLogger('zen.PythonWinSnmp')

# Service Operating state - 1 = active, continue-pending(2), pause-pending(3), paused(4)
# This is a column in an SNMP table

svSvcOperatingState = '1.3.6.1.4.1.77.1.2.3.1.3'
svSvcName = '1.3.6.1.4.1.77.1.2.3.1.1'

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


class SnmpWinServComponentDataSource(PythonDataSource):
    """ Get  operating state for each windows service using SNMP
        This is a component data source """
 
    ZENPACKID = 'ZenPacks.skills1st.WinSnmp'
 
    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('SnmpWinServComponentDataSource',)
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

    cycletime = 120
    #cycletime = 300

    _properties = PythonDataSource._properties + (
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'ipAddress', 'type': 'string', 'mode': 'w'},
        {'id': 'snmpVer', 'type': 'string', 'mode': 'w'},
        {'id': 'snmpCommunity', 'type': 'string', 'mode': 'w'},
    )

    # Collection plugin for this type. Defined below in this file.
    plugin_classname = ZENPACKID + '.datasources.SnmpWinServComponentDataSource.SnmpWinServComponentPlugin'
    # 
    def addDataPoints(self):
        if not self.datapoints._getOb('svSvcOperatingState', None):
            self.manage_addRRDDataPoint('svSvcOperatingState')

class ISnmpWinServComponentDataSourceInfo(IRRDDataSourceInfo):
    """Interface that creates the web form for this data source type."""
 
    hostname = schema.TextLine(
        title=_t(u'Host Name'),
        group=_t('SnmpWinServComponentDataSource'))
    ipAddress = schema.TextLine(
        title=_t(u'IP Address'),
        group=_t('SnmpWinServComponentDataSource'))
    snmpVer = schema.TextLine(
        title=_t(u'SNMP Version'),
        group=_t('SnmpWinServComponentDataSource'))
    snmpCommunity = schema.TextLine(
        title=_t(u'SNMP Community'),
        group=_t('SnmpWinServComponentDataSource'))

    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))
 
 
class SnmpWinServComponentDataSourceInfo(RRDDataSourceInfo):
    """Adapter between ISnmpWinServComponentDataSourceInfo and SnmpWinServComponentDataSource."""
 
    implements(ISnmpWinServComponentDataSourceInfo)
    adapts(SnmpWinServComponentDataSource)
 
    hostname = ProxyProperty('hostname')
    ipAddress = ProxyProperty('ipAddress')
    snmpVer = ProxyProperty('snmpVer')
    snmpCommunity = ProxyProperty('snmpCommunity')

    cycletime = ProxyProperty('cycletime')

    # Doesn't seem to run in the GUI if you activate the test button
    testable = False
    #testable = True
 
class SnmpWinServComponentPlugin(PythonDataSourcePlugin):
    """
    Collection plugin class for SnmpWinServComponentDataSource.
 
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
        d=getTableStuff(self._snmp_proxy, [ svSvcOperatingState, svSvcName,]) 
        # process here to get ..............
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

        # Format of result output is a dict of dicts with { oid:value } - INCLUDING leading dot !!
        #       svSvcOperatingState = '1.3.6.1.4.1.77.1.2.3.1.3'
        #  {'1.3.6.1.4.1.77.1.2.3.1.3': {'.1.3.6.1.4.1.77.1.2.3.1.3.22.67.114.121.112.116.111.103.114.97.112.104.105.99.32.83.101.114.118.105.99.101.115': 1, '.1.3.6.1.4.1.77.1.2.3.1.3.17.84.101.114.109.105.110.97.108.32.83.101.114.118.105.99.101.115': 1, ......   }
        # {'1.3.6.1.4.1.77.1.2.3.1.1': {'.1.3.6.1.4.1.77.1.2.3.1.1.11.87.111.114.107.115.116.97.116.105.111.110': 'Workstation', .....}}
        # Index into the component is the OID after 1.3.6.1.4.1.77.1.2.3.1.3
        # Eg. 22.67.114.121.112.116.111.103.114.97.112.104.105.99.32.83.101.114.118.105.99.101.115
        #  Which is the decimal ASCII for the service name

        datapointDict = {}
        valuepointDict = {}
        for k,v in result[svSvcName].iteritems():
            # Get the index part of the OID as a string, no leading or trailing dot
            # v is the string representing the service name
            # This gives datapointDict as {'23.69.114.114.111.114.32.82.101.112.111.114.116.105.110.103.32.83.101.114.118.105.99.101': 'Error Reporting Service', '12.83.78.77.80.32.83.101.114.118.105.99.101': 'SNMP Service',  ...........}

            oidIndex = '.'.join(k.split('.')[13:])
            # The component name may have gone through prepId to eliminate dangerous character
            #   so we need to do the same to the name here.
            v=prepId(v)
            datapointDict[oidIndex] = v
            #log.debug(' datapointDict is %s \n ' % (datapointDict))

            # Now get the svSvcOperatingState dict and construct valuepointDict which has
            #      { <service name> : <service operating status>, ......}
            #  eg. {'SNMP Service': 1, 'COM_ Event System': 1, 'Network Connections': 1, ......}

            for k1, v1 in result[svSvcOperatingState].iteritems():
                oidIndex1 = '.'.join(k1.split('.')[13:])
                if oidIndex == oidIndex1:
                    #log.debug('oidIndex1 is %s \n' % (oidIndex1))
                    valuepointDict[datapointDict[oidIndex1]] = v1

        log.debug(' valuepointDict is %s \n ' % (valuepointDict))

        for ds in config.datasources:
        #self.component = ds.component
            log.debug('ds is %s and ds.component is %s \n' % (ds, ds.component))
            # If the service has stopped running then the SNMP get table doesn't get a row entry for that service
            #   so next line will fail - try/except the failure and set the value to 0 = Stopped
            try:
                data['values'][ds.component] = { 'svSvcOperatingState' : valuepointDict[ds.component]}
            except:
                data['values'][ds.component] = { 'svSvcOperatingState' : 0 }

        # You don't have to provide an event - comment this out if so
        data['events'].append({
                    'device': config.id,
                    'summary': 'component service data gathered using zenpython with snmp',
                    'severity': 1,
                    'eventClass': '/App',
                    'eventKey': 'PythonSnmpWinServComponent',
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
                'summary': 'Error getting Snmp component services data with zenpython: %s' % result,
                'eventKey': 'PythonSnmpWinServComponent',
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

