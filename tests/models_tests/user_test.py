from tests import OhmTestCase


class UserTest(OhmTestCase):
    def test_get_multi(self):
        assert self.chuck.get_multi("PHONE") == ['+14086441234', '+14086445678']
        assert self.justin.get_multi("PHONE") == []

    def test_is_below_tier(self):
        # justin is on silver as per new migration
        assert self.justin.is_below_tier("Gold")
        assert not self.justin.is_below_tier("Carbon")

    def test_point_balance(self):
        # chuck has balance 5000
        assert self.chuck.point_balance == 5000

    def test_elvis_location(self):
        # elvis has location USA
        assert self.elvis.get_rel_user_attribute("LOCATION").attribute == "USA"