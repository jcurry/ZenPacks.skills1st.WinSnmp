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
import traceback
 
# Setup logging
import logging
log = logging.getLogger('zen.PythonWinSnmp')

hrProcessorLoad = '1.3.6.1.2.1.25.3.3.1.2'

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


class SnmpCpuDataSource(PythonDataSource):
    """ Get  RAM and Paging data for Windows devices
        using SNMP """
 
    ZENPACKID = 'ZenPacks.skills1st.WinSnmp'
 
    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('SnmpCpuDataSource',)
    sourcetype = sourcetypes[0]
 
    component = '${here/id}'
    eventClass = '/Perf/CPU'

    # Custom fields in the datasource - with default values
    #    (which can be overriden in template )
    hostname = '${dev/id}'
    ipAddress = '${dev/manageIp}'
    snmpVer = '${dev/zSnmpVer}'
    snmpCommunity = '${dev/zSnmpCommunity}'
    # cycle is redundant here - cycletime is standard and defaults to 300
    #cycle = '${here/cycle}'

    cycletime = 120

    _properties = PythonDataSource._properties + (
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'ipAddress', 'type': 'string', 'mode': 'w'},
        {'id': 'snmpVer', 'type': 'string', 'mode': 'w'},
        {'id': 'snmpCommunity', 'type': 'string', 'mode': 'w'},
    )

    # Collection plugin for this type. Defined below in this file.
    plugin_classname = ZENPACKID + '.datasources.SnmpCpuDataSource.SnmpCpuPlugin'
 

    def addDataPoints(self):
        if not self.datapoints._getOb('CPU1', None):
            self.manage_addRRDDataPoint('CPU1')
        if not self.datapoints._getOb('CPU2', None):
            self.manage_addRRDDataPoint('CPU2')
        if not self.datapoints._getOb('CPU3', None):
            self.manage_addRRDDataPoint('CPU3')
        if not self.datapoints._getOb('CPU4', None):
            self.manage_addRRDDataPoint('CPU4')
        if not self.datapoints._getOb('CPU5', None):
            self.manage_addRRDDataPoint('CPU5')
        if not self.datapoints._getOb('CPU6', None):
            self.manage_addRRDDataPoint('CPU6')
        if not self.datapoints._getOb('CPU7', None):
            self.manage_addRRDDataPoint('CPU7')
        if not self.datapoints._getOb('CPU8', None):
            self.manage_addRRDDataPoint('CPU8')
        if not self.datapoints._getOb('CPU9', None):
            self.manage_addRRDDataPoint('CPU9')
        if not self.datapoints._getOb('CPU10', None):
            self.manage_addRRDDataPoint('CPU10')
        if not self.datapoints._getOb('CPU11', None):
            self.manage_addRRDDataPoint('CPU11')
        if not self.datapoints._getOb('CPU12', None):
            self.manage_addRRDDataPoint('CPU12')
        if not self.datapoints._getOb('CPU13', None):
            self.manage_addRRDDataPoint('CPU13')
        if not self.datapoints._getOb('CPU14', None):
            self.manage_addRRDDataPoint('CPU14')
        if not self.datapoints._getOb('CPU15', None):
            self.manage_addRRDDataPoint('CPU15')
        if not self.datapoints._getOb('CPU16', None):
            self.manage_addRRDDataPoint('CPU16')
        if not self.datapoints._getOb('Total', None):
            self.manage_addRRDDataPoint('Total')

class ISnmpCpuDataSourceInfo(IRRDDataSourceInfo):
    """Interface that creates the web form for this data source type."""
 
    #cycle = schema.TextLine(title=_t(u'My Cycle (seconds)'))
    hostname = schema.TextLine(
        title=_t(u'Host Name'),
        group=_t('SnmpCpuDataSource'))
    ipAddress = schema.TextLine(
        title=_t(u'IP Address'),
        group=_t('SnmpCpuDataSource'))
    snmpVer = schema.TextLine(
        title=_t(u'SNMP Version'),
        group=_t('SnmpCpuDataSource'))
    snmpCommunity = schema.TextLine(
        title=_t(u'SNMP Community'),
        group=_t('SnmpCpuDataSource'))

    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))
 
 
class SnmpCpuDataSourceInfo(RRDDataSourceInfo):
    """Adapter between ISnmpCpuDataSourceInfo and SnmpCpuDataSource."""
 
    implements(ISnmpCpuDataSourceInfo)
    adapts(SnmpCpuDataSource)
 
    #cycle = ProxyProperty('cycle')
    hostname = ProxyProperty('hostname')
    ipAddress = ProxyProperty('ipAddress')
    snmpVer = ProxyProperty('snmpVer')
    snmpCommunity = ProxyProperty('snmpCommunity')

    cycletime = ProxyProperty('cycletime')

    # Doesn't seem to run in the GUI if you activate the test button
    testable = False
    #testable = True
 
class SnmpCpuPlugin(PythonDataSourcePlugin):
    """
    Collection plugin class for SnmpCpuDataSource.
 
    """
 
    # List of device attributes you'll need to do collection.
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
        try:
            self._snmp_proxy = get_snmp_proxy(ds0, config)
            # NB NB NB - When getting scalars, they must all come from the SAME snmp table
            # Now get data - 1 scalar OIDs
            d=getTableStuff(self._snmp_proxy, [ hrProcessorLoad,])
            #self._snmp_proxy.close()
            return d
        except Exception:
            log.warn('Exception in collect %s ' % (traceback.format_exc()))



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

        """

        log.debug( 'In success - result is %s and config is %s ' % (result, config))
        # Next line creates a dictionary like 
        #          {'values': defaultdict(<type 'dict'>, {}), 'events': [], 'maps':[]}
        # the new_data method is defined in PythonDataSource.py in the Python Collector
        #     ZenPack, datasources directory

        data = self.new_data()
        ds0 = config.datasources[0]

        log.debug( 'In success - data is %s  ' % (data))
        # Format of output in script result is
        # {'1.3.6.1.2.1.25.3.3.1.2': {'.1.3.6.1.2.1.25.3.3.1.2.3': 0, '.1.3.6.1.2.1.25.3.3.1.2.2': 0}}
        cpu_index = 1
        total = 0
        datapointDict={}
        if len(result) > 0:
            for k,v in result[hrProcessorLoad].iteritems():
                #log.debug('k is %s and v is %s \n' % (k,v))
                datapointDict['CPU' + str(cpu_index)] = v
                total = total + v
                cpu_index += 1
            datapointDict['Total'] = total

        log.debug('datapointDict is %s \n ' % (datapointDict))
        data['values'] = {
                None : datapointDict
                }

        # You don't have to provide an event - comment this out if so
        #data['events'].append({
        #            'device': config.id,
        #            'summary': 'Snmp cpu data gathered using zenpython with SNMP',
        #            'severity': 1,
        #            'eventClass': '/App',
        #            'eventKey': 'PythonSnmpCpu',
        #            })

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
                'summary': 'Error getting Snmp cpu data with zenpython and SNMP: %s' % result,
                'eventKey': 'PythonSnmpCpu',
                'severity': 4,
                }],
            }
 
    def onComplete(self, result, config):
        """
        Called last for success and error.
 
        You can omit this method if you want the result of either the
        onSuccess or onError method to be used without further processing.
        """
        try:
            if self._snmp_proxy:
                self._snmp_proxy.close()
        except:
            log.debug( ' In except in onComplete')
        return result

