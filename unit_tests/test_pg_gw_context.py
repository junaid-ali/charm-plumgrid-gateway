from test_utils import CharmTestCase
from mock import patch
import pg_gw_context as context
import pg_gw_utils as utils
import charmhelpers

TO_PATCH = [
    'get_unit_hostname',
]


def fake_context(settings):
    def outer():
        def inner():
            return settings
        return inner
    return outer


class PGGwContextTest(CharmTestCase):

    def setUp(self):
        super(PGGwContextTest, self).setUp(context, TO_PATCH)

    def tearDown(self):
        super(PGGwContextTest, self).tearDown()

    @patch.object(context.PGGwContext, '_ensure_packages')
    @patch.object(charmhelpers.contrib.openstack.context, 'https')
    @patch.object(charmhelpers.contrib.openstack.context, 'is_clustered')
    @patch.object(charmhelpers.contrib.openstack.context, 'config')
    @patch.object(charmhelpers.contrib.openstack.context, 'unit_private_ip')
    @patch.object(charmhelpers.contrib.openstack.context, 'unit_get')
    @patch.object(charmhelpers.contrib.openstack.context,
                  'config_flags_parser')
    @patch.object(context.PGGwContext, '_save_flag_file')
    @patch.object(context, '_pg_dir_settings')
    @patch.object(charmhelpers.contrib.openstack.context,
                  'neutron_plugin_attribute')
    @patch.object(utils, 'get_mgmt_interface')
    @patch.object(utils, 'get_fabric_interface')
    @patch.object(utils, 'get_gw_interfaces')
    def test_neutroncc_context_api_rel(self, _gw_int, _fabric_int,
                                       _mgmt_int, _npa, _pg_dir_settings,
                                       _save_flag_file, _config_flag,
                                       _unit_get, _unit_priv_ip, _config,
                                       _is_clus, _https, _ens_pkgs):
        def mock_npa(plugin, section, manager):
            if section == "driver":
                return "neutron.randomdriver"
            if section == "config":
                return "neutron.randomconfig"

        self.maxDiff = None
        _npa.side_effect = mock_npa
        _unit_get.return_value = '192.168.100.201'
        _unit_priv_ip.return_value = '192.168.100.201'
        self.get_unit_hostname.return_value = 'node0'
        _is_clus.return_value = False
        _config_flag.return_value = False
        _pg_dir_settings.return_value = {'pg_dir_ip': '192.168.100.201'}
        _mgmt_int.return_value = 'juju-br0'
        _fabric_int.return_value = 'juju-br0'
        _gw_int.return_value = ['eth1']
        napi_ctxt = context.PGGwContext()
        expect = {
            'ext_interfaces': ['eth1'],
            'config': 'neutron.randomconfig',
            'core_plugin': 'neutron.randomdriver',
            'local_ip': 'pg_dir_ip',
            'network_manager': 'neutron',
            'neutron_plugin': 'plumgrid',
            'neutron_security_groups': None,
            'neutron_url': 'https://192.168.100.201:9696',
            'pg_hostname': 'node0',
            'interface': 'juju-br0',
            'fabric_interface': 'juju-br0',
            'label': 'node0',
            'fabric_mode': 'host',
            'neutron_alchemy_flags': False,
        }
        self.assertEquals(expect, napi_ctxt())
