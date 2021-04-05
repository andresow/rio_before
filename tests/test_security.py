from odoo.tests.common import TransactionCase, tagged

@tagged('-at_install', 'post_install')
class TestSecurity(TransactionCase):

    def setUp(self, *args, **kwargs): 
        super(TestSecurity, self).setUp(*args, **kwargs) 
        self.report = self.env['security.report'].create({
            'date': '2020-10-10',
            'date_action': '2020-10-10',
            'position': 'Desarollador',
            'direction': 'av empresrios 35',
            'cordenates': '30,30',
            'actions': 'TEST',
            'state': 'generate'
        })


    def test_update_state_asign(self):

        self.report.update_state_asign()

    def test_finish_RIO(self):

        self.report.finish_RIO()