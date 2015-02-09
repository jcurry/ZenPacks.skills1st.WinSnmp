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

class CmdSnmpCpuDataSource(PythonDataSource):
    """ Get  CPU data for Windows devices
        using SNMP """
 
    ZENPACKID = 'ZenPacks.skills1st.WinSnmp'
 
    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('CmdSnmpCpuDataSource',)
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
    plugin_classname = ZENPACKID + '.datasources.CmdSnmpCpuDataSource.CmdSnmpCpuPlugin'
 

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
        if not self.datapoints._getOb('CPU1', None):
            self.manage_addRRDDataPoint('CPU1')
        if not self.datapoints._getOb('Total', None):
            self.manage_addRRDDataPoint('Total')

class ICmdSnmpCpuDataSourceInfo(IRRDDataSourceInfo):
    """Interface that creates the web form for this data source type."""
 
    #cycle = schema.TextLine(title=_t(u'My Cycle (seconds)'))
    hostname = schema.TextLine(
        title=_t(u'Host Name'),
        group=_t('CmdSnmpCpuDataSource'))
    ipAddress = schema.TextLine(
        title=_t(u'IP Address'),
        group=_t('CmdSnmpCpuDataSource'))
    snmpVer = schema.TextLine(
        title=_t(u'SNMP Version'),
        group=_t('CmdSnmpCpuDataSource'))
    snmpCommunity = schema.TextLine(
        title=_t(u'SNMP Community'),
        group=_t('CmdSnmpCpuDataSource'))

    cycletime = schema.TextLine(
        title=_t(u'Cycle Time (seconds)'))
 
 
class CmdSnmpCpuDataSourceInfo(RRDDataSourceInfo):
    """Adapter between ICmdSnmpCpuDataSourceInfo and CmdSnmpCpuDataSource."""
 
    implements(ICmdSnmpCpuDataSourceInfo)
    adapts(CmdSnmpCpuDataSource)
 
    #cycle = ProxyProperty('cycle')
    hostname = ProxyProperty('hostname')
    ipAddress = ProxyProperty('ipAddress')
    snmpVer = ProxyProperty('snmpVer')
    snmpCommunity = ProxyProperty('snmpCommunity')

    cycletime = ProxyProperty('cycletime')

    # Doesn't seem to run in the GUI if you activate the test button
    testable = False
    #testable = True
 
class CmdSnmpCpuPlugin(PythonDataSourcePlugin):
    """
    Collection plugin class for CmdSnmpCpuDataSource.
 
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

        # script is wincpu.py taking 3 parameters, hostname or IP, zSnmpVer, zSnmpCommunity
        cmdparts = [ os.path.join(libexecdir, 'wincpu.py') ]

        # context is the object that the template is applied to  - either a device or a component
        #  In this case it is a device with all the attributes and methods of a device

        if context.titleOrId():
            cmdparts.append(context.titleOrId())
        elif context.manageIp:
            cmdparts.append(context.manageIp)
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

        # script is wincpu.py taking 3 parameters, hostname or IP, zSnmpVer, zSnmpCommunity
        cmd = [ os.path.join(libexecdir, 'wincpu.py'), ds0.manageIp, ds0.zSnmpVer, ds0.zSnmpCommunity ]
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
        ds0 = config.datasources[0]

        log.debug( 'In success - data is %s  ' % (data))
        # Format of output in script result is
        # OK|CPU1=38 CPU2=37 Total=37
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
                    'summary': 'Snmp CPU data gathered using zenpython with wincpu script',
                    'severity': 1,
                    'eventClass': '/App',
                    'eventKey': 'PythonCmdSnmpCpu',
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
                'summary': 'Error getting Snmp CPU data with zenpython: %s' % result,
                'eventKey': 'PythonCmdSnmpCpu',
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

