import pytest

from testing.snmp_responder import AuthenticationInformation, MockedSynologyMibController, SnmpResponder


@pytest.fixture
def synology_mock():

    auth_info = AuthenticationInformation(
        userName="test-user",
        authProtocol="MD5",
        authKey="test-authkey",
        privProtocol="AES128",
        privKey="test-privkey",
    )

    snmpd = SnmpResponder(port=1161, auth_info=auth_info)
    # snmpd = SnmpResponder(port=1161, debug_flags=["all"])
    # snmpd = SnmpResponder(port=1161, debug_flags=["dsp", "msgproc", "secmod"])

    snmpd.setup()
    snmpd.create_context(MockedSynologyMibController())
    snmpd.start_background()

    yield snmpd

    snmpd.stop()
