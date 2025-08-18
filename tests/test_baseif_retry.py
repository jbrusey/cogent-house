import sys
from unittest.mock import MagicMock, patch

# Access stub module prepared in conftest
moteif_mod = sys.modules["tinyos3.message.MoteIF"]
MoteIFClass = MagicMock()
moteif_mod.MoteIF = MoteIFClass

from pulp.base.BaseIF import BaseIF


def test_retry_on_connection_refused():
    mif_instance = MagicMock()
    source_obj = MagicMock()
    mif_instance.addSource.side_effect = [ConnectionRefusedError, source_obj]
    MoteIFClass.return_value = mif_instance

    with patch("time.sleep") as sleep:
        BaseIF("sf@localhost:9002", retries=2, retry_delay=0.1)

    assert mif_instance.addSource.call_count == 2
    sleep.assert_called_once()
