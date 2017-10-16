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

hrStorageType = '1.3.6.1.2.1.25.2.3.1.2'
hrStorageAllocationUnits = '1.3.6.1.2.1.25.2.3.1.4'
hrStorageSize = '1.3.6.1.2.1.25.2.3.1.5'
hrStorageUsed = '1.3.6.1.2.1.25.2.3.1.6'

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
    log.debug('In getTableStuff - snmp_proxy is %s and scalarOIDstrings is %s \n' % (snmp_proxy, OIDstrings))
    d=snmp_proxy.getTable(OIDstrings)
    return d


class SnmpMemDataSource(PythonDataSource):
    """ Get  RAM and Paging data for Windows devices
        using SNMP """
 
    ZENPACKID = 'ZenPacks.skills1st.WinSnmp'
 
    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('SnmpMemDataSource',)
    sourcetype = sourcetypes[0]
 
    component = '${here/id}'
    eventClass = '/Perf/Memory/Snmp'

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
    plugin_classname = ZENPACKID + '.datasources.SnmpMemDataSource.SnmpMemPlugin'
 

    def addDataPoints(self):
        if not self.datapoints._getOb('MemoryTotal', None):
            self.manage_addRRDDataPoint('MemoryTotal')
        if not self.datapoints._getOb('MemoryUsed', None):
            self.manage_addRRDDataPoint('MemoryUsed')
        if not self.datapoints._getOb('PercentMemoryUsed', None):
            self.manage_addRRDDataPoint('PercentMemoryUsed')
        if not self.datapoints._getOb('PagingTotal', None):
            self.manage_addRRDDataPoint('PagingTotal')
        if not self.datapoints._getOb('PagingUsed', None):
            dp=self.manage_addRRDDataPoint('PagingUsed')
            dp.rrdtype = 'DERIVE'
            dp.rrdmin = 0
            dp.rrdmax = None       # NB. rrdmin MUST be less than rrdmax or zenpython will barf on storing rrd data
            dp.description = 'Paging Used as a counter'
        if not self.datapoints._getOb('PercentPagingUsed', None):
            self.manage_addRRDDataPoint('PercentPagingUsed')

class ISnmpMemDataSourceInfo(IRRDDataSourceInfo):
    """Interface that creates the web form for this data source type."""
 
    #cycle = schema.TextLine(title=_t(u'My Cycle (seconds)'))
    hostname = schema.TextLine(
        title=_t(u'Host Name'),
        group=_t('SnmpMemDataSource'))
    ipAddress = schema.TextLine(
        title=_t(u'IP Address'),
        group=_t('SnmpMemDataSource'))
    snmpVer = schema.TextLine(
        title=_t(u'SNMP Version'),
        group=_t('SnmpMemDataSource'))
    snmpCommunity = schema.TextLine(
        title=_t(u'SNMP Community'),
        group=_t('SnmpMemDataSource'))

    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))
 
 
class SnmpMemDataSourceInfo(RRDDataSourceInfo):
    """Adapter between ISnmpMemDataSourceInfo and SnmpMemDataSource."""
 
    implements(ISnmpMemDataSourceInfo)
    adapts(SnmpMemDataSource)
 
    #cycle = ProxyProperty('cycle')
    hostname = ProxyProperty('hostname')
    ipAddress = ProxyProperty('ipAddress')
    snmpVer = ProxyProperty('snmpVer')
    snmpCommunity = ProxyProperty('snmpCommunity')

    cycletime = ProxyProperty('cycletime')

    # Doesn't seem to run in the GUI if you activate the test button
    testable = False
    #testable = True
 
class SnmpMemPlugin(PythonDataSourcePlugin):
    """
    Collection plugin class for SnmpMemDataSource.
 
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
        self._snmp_proxy = get_snmp_proxy(ds0, config)
        d = getTableStuff(self._snmp_proxy, [hrStorageType, hrStorageAllocationUnits, hrStorageSize, hrStorageUsed, ] )
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
        # 
        # get hrStorageType dict first and get instance num for hrStorageRam and hrStorageVirtualMemory
        # We get untranslated StorageType ie numbers where last number 2 - RAM and last number 3 = Virtual Memory
        # We need to get the instance of the OID to use as an index into allocation units, etc
        hrStorageRamTypeOid = '.1.3.6.1.2.1.25.2.1.2'
        hrStorageVirtMemTypeOid = '.1.3.6.1.2.1.25.2.1.3'

        StorageType = result[hrStorageType]
        oid_mem = None
        oid_paging = None

        log.debug('StorageType is %s \n' % (StorageType))
        for k,v in StorageType.iteritems():
            #log.debug('k is %s and v is %s \n' % (k,v))
            if v == hrStorageRamTypeOid:
                oid_mem = k.split('.')[-1]
            elif v == hrStorageVirtMemTypeOid:
                oid_paging = k.split('.')[-1]
        
        if oid_mem and oid_paging:
            usage_mem = result[hrStorageUsed]['.'+ hrStorageUsed + '.' + oid_mem]
            total_mem = result[hrStorageSize]['.'+ hrStorageSize + '.' + oid_mem]
            units_mem = result[hrStorageAllocationUnits]['.'+ hrStorageAllocationUnits + '.' + oid_mem]
            usage_paging = result[hrStorageUsed]['.'+ hrStorageUsed + '.' + oid_paging]
            total_paging = result[hrStorageSize]['.'+ hrStorageSize + '.' + oid_paging]
            units_paging = result[hrStorageAllocationUnits]['.'+ hrStorageAllocationUnits + '.' + oid_paging]

            
        datapointDict={}
        datapointDict['MemoryTotal'] = total_mem * units_mem / 1.024
        datapointDict['MemoryUsed'] = usage_mem * units_mem / 1.024
        datapointDict['PercentMemoryUsed'] = usage_mem / total_mem * 100
        datapointDict['PagingTotal'] = total_paging * units_paging / 1.024
        datapointDict['PagingUsed'] = usage_paging * units_paging / 1.024
        datapointDict['PercentPagingUsed'] = usage_paging / total_paging * 100

        log.debug('datapointDict is %s \n ' % (datapointDict))
        data['values'] = {
                None : datapointDict
                }

        # You don't have to provide an event - comment this out if so
        #data['events'].append({
        #            'device': config.id,
        #            'summary': 'Snmp memory data gathered using zenpython with SNMP',
        #            'severity': 1,
        #            'eventClass': '/App',
        #            'eventKey': 'PythonSnmpMem',
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
                'summary': 'Error getting Snmp memory data with zenpython and SNMP: %s' % result,
                'eventKey': 'PythonSnmpMem',
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

