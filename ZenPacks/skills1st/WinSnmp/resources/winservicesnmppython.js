(function(){

var ZC = Ext.ns('Zenoss.component');


function render_link(ob) {
    if (ob && ob.uid) {
        return Zenoss.render.link(ob.uid);
    } else {
        return ob;
    }
}

ZC.WinServiceSNMPPythonPanel = Ext.extend(ZC.ComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'WinServiceSNMPPython',
             fields: [
                 {name: 'uid'},
                 {name: 'name'},
                 {name: 'severity'},
                 {name: 'status'},
                 {name: 'hasMonitor'},
                 {name: 'usesMonitorAttribute'},
                 {name: 'monitor'},
                 {name: 'monitored'},
                 {name: 'locking'}
             ],
             columns: [{
                 id: 'severity',
                 dataIndex: 'severity',
                 header: _t('Events'),
                 renderer: Zenoss.render.severity,
                 width: 60
             },{
                id: 'name',
                 dataIndex: 'name',
                 header: _t('Name'),
                 width: 120,
                 sortable: true,
                 flex: 1
             },{
                 id: 'status',
                 dataIndex: 'status',
                 header: _t('Status'),
                 renderer: Zenoss.render.pingStatus,
                 width: 60
             },{
                 id: 'monitored',
                 dataIndex: 'monitored',
                 header: _t('Monitored'),
                 width: 70,
                 sortable: true
             },{
                 id: 'locking',
                 dataIndex: 'locking',
                 header: _t('Locking'),
                 width: 72,
                 renderer: Zenoss.render.locking_icons
             }]
         });
        ZC.WinServiceSNMPPythonPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('WinServiceSNMPPythonPanel', ZC.WinServiceSNMPPythonPanel);
ZC.registerName('WinServiceSNMPPython', _t('WinServiceSNMPPython Interface'), _t('SNMP Python Windows Services'));
})();


