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

hrSystemProcesses = '.1.3.6.1.2.1.25.1.6.0'
hrSystemMaxProcesses = '.1.3.6.1.2.1.25.1.7.0'

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
    # NB OIDs in scalarOIDstrings MUST all be in the same SNMP table or you get no data returned
    # NB Windows net-snmp agent 5.5.0-1 return null dictionary if
    #     input list is > 1 oid - maybe ?????
    # Agent Proxy get returns dict of {oid_str : <value>}
    log.debug('In getScalarStuff - snmp_proxy is %s and scalarOIDstrings is %s \n' % (snmp_proxy, scalarOIDstrings))
    d=snmp_proxy.get(scalarOIDstrings)
    return d

def getTableStuff(snmp_proxy, OIDstrings):
    d=snmp_proxy.getTable(OIDstrings)
    return d


class SnmpProcDataSource(PythonDataSource):
    """ Get  number of processes, max no. processes and number of services
        for Windows devices using SNMP """
 
    ZENPACKID = 'ZenPacks.skills1st.WinSnmp'
 
    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('SnmpProcDataSource',)
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
    plugin_classname = ZENPACKID + '.datasources.SnmpProcDataSource.SnmpProcPlugin'
    # 
    def addDataPoints(self):
        if not self.datapoints._getOb('hrSystemProcesses', None):
            self.manage_addRRDDataPoint('hrSystemProcesses')
        if not self.datapoints._getOb('hrSystemMaxProcesses', None):
            self.manage_addRRDDataPoint('hrSystemMaxProcesses')

class ISnmpProcDataSourceInfo(IRRDDataSourceInfo):
    """Interface that creates the web form for this data source type."""
 
    hostname = schema.TextLine(
        title=_t(u'Host Name'),
        group=_t('SnmpProcDataSource'))
    ipAddress = schema.TextLine(
        title=_t(u'IP Address'),
        group=_t('SnmpProcDataSource'))
    snmpVer = schema.TextLine(
        title=_t(u'SNMP Version'),
        group=_t('SnmpProcDataSource'))
    snmpCommunity = schema.TextLine(
        title=_t(u'SNMP Community'),
        group=_t('SnmpProcDataSource'))

    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))
 
 
class SnmpProcDataSourceInfo(RRDDataSourceInfo):
    """Adapter between ISnmpProcDataSourceInfo and SnmpProcDataSource."""
 
    implements(ISnmpProcDataSourceInfo)
    adapts(SnmpProcDataSource)
 
    hostname = ProxyProperty('hostname')
    ipAddress = ProxyProperty('ipAddress')
    snmpVer = ProxyProperty('snmpVer')
    snmpCommunity = ProxyProperty('snmpCommunity')

    cycletime = ProxyProperty('cycletime')

    # Doesn't seem to run in the GUI if you activate the test button
    testable = False
    #testable = True
 
class SnmpProcPlugin(PythonDataSourcePlugin):
    """
    Collection plugin class for SnmpProcDataSource.
 
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
        # Now get data - 2 scalar OIDs
        d=getScalarStuff(self._snmp_proxy, [ hrSystemProcesses, hrSystemMaxProcesses, ]) 
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
 
        """

        log.debug( 'In success - result is %s and config is %s ' % (result, config))
        # Next line creates a dictionary like 
        #          {'values': defaultdict(<type 'dict'>, {}), 'events': [], 'maps':[]}
        # the new_data method is defined in PythonDataSource.py in the Python Collector
        #     ZenPack, datasources directory

        data = self.new_data()

        # Format of result output is a dict with { oid:value } - INCLUDING leading dot !!
        #       hrSystemProcesses = '.1.3.6.1.2.1.25.1.6.0'
        #       hrSystemMaxProcesses = '.1.3.6.1.2.1.25.1.7.0'
        # Remember datapoint names are hrSystemProcesses, hrSystemMaxProcesses
        # This is being kind to users giving them datapoints that are somewhat meaningful
        # If you want to be cruel, define the datapoints as the OID string and simply return
        #   the results dictionary

        datapointDict = {}
        for k,v in result.iteritems():
            if k == hrSystemProcesses:
                datapointDict['hrSystemProcesses'] = v
            elif k == hrSystemMaxProcesses:
                datapointDict['hrSystemMaxProcesses'] = v

        log.debug('datapointDict is %s \n ' % (datapointDict))
        data['values'] = {
                None : datapointDict
                }

        # You don't have to provide an event - comment this out if so
        #data['events'].append({
        #            'device': config.id,
        #            'summary': 'process data gathered using zenpython with snmp',
        #            'severity': 1,
        #            'eventClass': '/App',
        #            'eventKey': 'PythonSnmpProc',
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
                'summary': 'Error getting Snmp process data with zenpython: %s' % result,
                'eventKey': 'PythonSnmpProc',
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

