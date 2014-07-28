import proboscis

from fuelweb_test.helpers.decorators import log_snapshot_on_error
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
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
            6. Create and delete instance
        """
        logger.info("DBG! deploy_nsx start")
        self.env.revert_snapshot("ready_with_3_slaves")
        self.fuel_web.client.get_root()
        self.env.bootstrap_nodes(self.env.nodes().slaves[:1])
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__
            # mode=settings{
            # 'nsx':'aaa'
            # }
        )
        logger.info('cluster is %s' % str(cluster_id))
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['cinder'],
                'slave-03': ['compute']
            }
        )
        self.fuel_web.deploy_cluster_wait(cluster_id)
        # Run ostf
        self.fuel_web.run_ostf(cluster_id=cluster_id)
