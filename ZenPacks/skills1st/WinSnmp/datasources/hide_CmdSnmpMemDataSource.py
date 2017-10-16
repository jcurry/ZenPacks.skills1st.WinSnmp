from zope.component import adapts
from zope.interface import implements
 
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t
 
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSource, PythonDataSourcePlugin

import os
import subprocess
from twisted.internet import defer
 
# Setup logging
import logging
log = logging.getLogger('zen.PythonWinSnmp')

class CmdSnmpMemDataSource(PythonDataSource):
    """ Get  RAM and Paging data for Windows devices
        using SNMP """
 
    ZENPACKID = 'ZenPacks.skills1st.WinSnmp'
 
    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('CmdSnmpMemDataSource',)
    sourcetype = sourcetypes[0]
 
    component = '${here/id}'
    eventClass = '/Perf/Memory/Snmp'
    # cycletime is standard and defaults to 300
    cycletime = 120

    # Custom fields in the datasource - with default values
    #    (which can be overriden in template )
    hostname = '${dev/id}'
    ipAddress = '${dev/manageIp}'
    snmpVer = '${dev/zSnmpVer}'
    snmpCommunity = '${dev/zSnmpCommunity}'

    _properties = PythonDataSource._properties + (
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'ipAddress', 'type': 'string', 'mode': 'w'},
        {'id': 'snmpVer', 'type': 'string', 'mode': 'w'},
        {'id': 'snmpCommunity', 'type': 'string', 'mode': 'w'},
    )

    # Collection plugin for this type. Defined below in this file.
    plugin_classname = ZENPACKID + '.datasources.CmdSnmpMemDataSource.CmdSnmpMemPlugin'
 

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

class ICmdSnmpMemDataSourceInfo(IRRDDataSourceInfo):
    """Interface that creates the web form for this data source type."""
 
    #cycle = schema.TextLine(title=_t(u'My Cycle (seconds)'))
    hostname = schema.TextLine(
        title=_t(u'Host Name'),
        group=_t('CmdSnmpMemDataSource'))
    ipAddress = schema.TextLine(
        title=_t(u'IP Address'),
        group=_t('CmdSnmpMemDataSource'))
    snmpVer = schema.TextLine(
        title=_t(u'SNMP Version'),
        group=_t('CmdSnmpMemDataSource'))
    snmpCommunity = schema.TextLine(
        title=_t(u'SNMP Community'),
        group=_t('CmdSnmpMemDataSource'))

    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))
 
 
class CmdSnmpMemDataSourceInfo(RRDDataSourceInfo):
    """Adapter between ICmdSnmpMemDataSourceInfo and CmdSnmpMemDataSource."""
 
    implements(ICmdSnmpMemDataSourceInfo)
    adapts(CmdSnmpMemDataSource)
 
    #cycle = ProxyProperty('cycle')
    hostname = ProxyProperty('hostname')
    ipAddress = ProxyProperty('ipAddress')
    snmpVer = ProxyProperty('snmpVer')
    snmpCommunity = ProxyProperty('snmpCommunity')

    cycletime = ProxyProperty('cycletime')

    # Doesn't seem to run in the GUI if you activate the test button
    testable = False
    #testable = True
 
class CmdSnmpMemPlugin(PythonDataSourcePlugin):
    """
    Collection plugin class for CmdSnmpMemDataSource.
 
    """
 
    # List of device attributes you'll need to do collection.
    proxy_attributes = (
        'zSnmpVer',
        'zSnmpCommunity',
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
        params['snmpVer'] = datasource.talesEval(datasource.snmpVer, context)
        params['snmpCommunity'] = datasource.talesEval(datasource.snmpCommunity, context)

        # Get path to executable file, starting from this file
        #    which is in ZenPack base dir/datasources
        # Executables are in ZenPack base dir / libexec

        thisabspath = os.path.abspath(__file__)
        (filedir, tail) = os.path.split(thisabspath)
        libexecdir = filedir + '/../libexec'

        # script is winmem.py taking 3 parameters, hostname or IP, zSnmpVer, zSnmpCommunity
        cmdparts = [ os.path.join(libexecdir, 'winmem.py') ]

        # context is the object that the template is applied to  - either a device or a component
        #  In this case it is a device with all the attributes and methods of a device

        if context.manageIp:
            cmdparts.append(context.manageIp)
        elif context.titleOrId():
            cmdparts.append(context.titleOrId())
        else:
            cmdparts.append('UnknownHostOrIp')
        # This gets parameters from the template
        if not params['snmpVer']:
            cmdparts.append('v1')
        else:
            cmdparts.append(params['snmpVer'])
        if not params['snmpCommunity']:
            cmdparts.append('public')
        else:
            cmdparts.append(params['snmpCommunity'])

        """ 
        # This gets parameters direct from the device using context
        if not context.zSnmpVer:
            cmdparts.append('v1')
        else:
            cmdparts.append(context.zSnmpVer)
        if not context.zSnmpCommunity:
            cmdparts.append('public')
        else:
            cmdparts.append(context.zSnmpCommunity)
       """
            
        params['cmd'] = cmdparts           

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

        # Next 3 lines use params to get cmd
        cmd = ds0.params['cmd']
        log.debug(' cmd is %s \n ' % (cmd) )
        cmd_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        """
        # or this lot if you dont use params and do use device proxy attributes
        # Get path to executable file, starting from this file
        #    which is in ZenPack base dir/datasources
        # Executables are in ZenPack base dir / libexec

        thisabspath = os.path.abspath(__file__)
        (filedir, tail) = os.path.split(thisabspath)
        libexecdir = filedir + '/../libexec'

        # script is winmem.py taking 3 parameters, hostname or IP, zSnmpVer, zSnmpCommunity
        cmd = [ os.path.join(libexecdir, 'winmem.py'), ds0.manageIp, ds0.zSnmpVer, ds0.zSnmpCommunity ]
        log.debug(' cmd is %s \n ' % (cmd) )
        cmd_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        """

        cmd_out = cmd_process.communicate()
        dd = defer.Deferred()
        # cmd_process.communicate() returns a tuple of (stdoutdata, stderrordata)
        if cmd_process.returncode == 0:
            dd.callback(cmd_out[0])
        else:
            dd.errback(cmd_out[1])
        return dd

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

        log.debug( 'In success - data is %s  ' % (data))
        # Format of output in script result is
        # OK|MemoryTotal=523712000 MemoryUsed=213184000 PercentMemoryUsed=41 PagingTotal=1284096000 PagingUsed=190784000 PercentPagingUsed=15
        dataVarVals = result.split("|")[1].split()
        log.debug('split result is %s \n ' % (dataVarVals))
        datapointDict={}
        for d in dataVarVals:
            myvar,myval = d.split("=")
            datapointDict[myvar] = myval
        log.debug('datapointDict is %s \n ' % (datapointDict))
        data['values'] = {
                None : datapointDict
                }

        # You don't have to provide an event - comment this out if so
        data['events'].append({
                    'device': config.id,
                    'summary': 'Snmp memory data gathered using zenpython with winmem script',
                    'severity': 1,
                    'eventClass' : '/App',
                    'eventKey': 'PythonCmdSnmpMem',
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
                'summary': 'Error getting Snmp memory data with zenpython: %s' % result,
                'eventKey': 'PythonCmdSnmpMem',
                'severity': 4,
                }],
            }
 
    def onComplete(self, result, config):
        """
        Called last for success and error.
 
        You can omit this method if you want the result of either the
        onSuccess or onError method to be used without further processing.
        """
        return result

