import proboscis
from proboscis.asserts import assert_equal

from fuelweb_test.helpers.decorators import log_snapshot_on_error
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from fuelweb_test.settings import DEPLOYMENT_MODE_SIMPLE
import fuelweb_test.settings as help_data
from fuelweb_test import logger
from proboscis import test


@test(groups=["nsx"])
class NsxDeploy(TestBasic):
    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["smoke", "deploy_nsx"])
    @log_snapshot_on_error
    def deploy_nsx(self):
        """Deploy cluster with nsx network

        Scenario:
            1. Create cluster
            2. Add 1 node with controller role
            3. Add 1 node with cinder role
            4. Add 1 node with compute role
            5. Deploy the cluster
            6. Run ostf test which check connectivity to the floating IP using ping command.
        """
        logger.info("DBG! deploy_nsx start")
        self.env.revert_snapshot("ready_with_3_slaves")
        self.fuel_web.client.get_root()
        self.env.bootstrap_nodes(self.env.nodes().slaves[:1])
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE_SIMPLE,
            settings={
                'libvirt_type': 'qemu',
                'nsx_username': 'admin',
                'nsx_password': 'admin',
                'transport_zone_uuid': 'e0c69125-86cc-4118-888f-90dae8a5e1e8',
                'l3_gw_service_uuid': '365555e0-0400-46a9-b8c2-f02ab511220c',
                'nsx_controllers': '172.16.1.253',
                'packages_url': '172.16.1.1',
                'connector_type': 'stt',
                'tenant': 'nsx',
                'user': 'nsx',
                'password': 'nsx',
                'net_provider': 'neutron',
                'net_l23_provider': 'nsx',
                'net_segment_type': 'gre'
            },
            release_name=help_data.OPENSTACK_RELEASE
        )
        assert_equal(str(cluster['net_provider']), 'neutron')
        
        logger.info('cluster is %s' % str(cluster_id))
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['cinder'],
                'slave-03': ['compute']
            }
        )
        logger.info('DBG! deploy_cluster_wait')
        self.fuel_web.deploy_cluster_wait(cluster_id)
        logger.info('\e[32mDBG! run ostf\033[0m')
        # Run ostf
        self.fuel_web.run_ostf(cluster_id=cluster_id)
        self.fuel_web.run_single_ostf_test(
            cluster_id=cluster_id, test_sets=['smoke'],
            test_name=('fuel_health.tests.smoke.'
                       'test_nova_create_instance_with_connectivity.'
                       'TestNovaNetwork.test_008_check_public_instance_connectivity_from_instance'))
