
from app_main import app
from tests import OhmTestCase


class DashboardTest(OhmTestCase):
    def test_get(self):
        with app.test_client() as c:
            response = c.get('/dashboard')
            assert "Ready to begin assessment" in response.data
