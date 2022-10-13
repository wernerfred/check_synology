"""
About
=====

A custom MIB controller. Listen and respond to SNMP GET/SET/GETNEXT/GETBULK
queries with the following options:

* SNMPv3
* with USM username usr-none-none
* using alternative set of Managed Objects addressed by 
  contextName: my-context
* allow access to SNMPv2-MIB objects (1.3.6.1.2.1)
* over IPv4/UDP, listening at 127.0.0.1:161

The following Net-SNMP command will send GET request to this Agent::

    snmpget -v3 -u usr-none-none -l noAuthNoPriv -Ir localhost:1161 "1.3.6.1.4.1.2021.10.1.5.1"

Setup
=====
::

    pip install pysnmplib

References
==========
- https://github.com/pysnmp/pysnmp/blob/main/examples/v3arch/asyncore/agent/cmdrsp/custom-mib-controller.py
- https://github.com/pysnmp/pysnmp/blob/main/examples/v3arch/asyncore/agent/cmdrsp/multiple-usm-users.py
"""
import asyncio
import dataclasses
import sys
import threading
import typing as t
from enum import Enum

from pyasn1.compat.octets import null
from pysnmp import debug
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import config, engine
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.proto.api import v2c
from pysnmp.proto.secmod.rfc3414.auth.base import AbstractAuthenticationService
from pysnmp.proto.secmod.rfc3414.priv.base import AbstractEncryptionService
from pysnmp.smi import instrum


@dataclasses.dataclass
class AuthenticationInformation:
    userName: str
    authProtocol: t.Union[str, AbstractAuthenticationService]
    authKey: str
    privProtocol: t.Union[str, AbstractEncryptionService]
    privKey: str

    def __post_init__(self):
        if isinstance(self.authProtocol, str):
            if self.authProtocol == "MD5":
                self.authProtocol = config.usmHMACMD5AuthProtocol
            else:
                raise KeyError(f"Authentication protocol {self.authProtocol} not implemented")
        if isinstance(self.privProtocol, str):
            if self.privProtocol == "AES128":
                self.privProtocol = config.usmAesCfb128Protocol
            else:
                raise KeyError(f"Encryption protocol {self.privProtocol} not implemented")

    def asdict(self):
        return dataclasses.asdict(self)


class SnmpResponder:
    """
    A generic SNMP responder based on `pysnmplib`, using `asyncore`.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 161,
        auth_info: t.Optional[AuthenticationInformation] = None,
        debug_flags: t.Optional[t.List[str]] = None,
    ):

        self.host = host
        self.port = port
        self.auth_info = auth_info

        debug_flags = debug_flags or []
        if debug_flags:
            debug.setLogger(debug.Debug(*debug_flags))

        # Create SNMP engine
        self.snmp_engine = engine.SnmpEngine()

    def setup(self):
        # Transport setup

        # UDP over IPv4.
        # TODO: Make selecting different transport configurable.
        config.addTransport(
            snmpEngine=self.snmp_engine,
            transportDomain=udp.domainName,
            transport=udp.UdpTransport().openServerMode((self.host, self.port)),
        )

        # SNMPv3/USM setup

        # user: usr-none-none, auth: NONE, priv NONE
        # For testing with `snmpget`.
        """
        config.addV3User(
            snmpEngine=self.snmp_engine,
            userName='usr-none-none',
        )
        """

        # user: foo, auth: MD5, priv AES128
        if self.auth_info:
            config.addV3User(
                snmpEngine=self.snmp_engine,
                **self.auth_info.asdict(),
            )

        # Allow full MIB access for each user at VACM
        # config.addVacmUser(snmpEngine, 3, 'usr-none-none', 'noAuthNoPriv', (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))
        # config.addVacmUser(snmpEngine, 3, 'foo', 'authPriv', (1, 3, 6, 1, 2, 1), (1, 3, 6, 1, 2, 1))
        # config.addVacmUser(snmpEngine, 3, 'foo', 'authPriv', (1, 3, 6, 1, 4, 1), (1, 3, 6, 1, 4, 1))

    def create_context(self, controller: instrum.AbstractMibInstrumController = None):

        # Create an SNMP context
        snmp_context = context.SnmpContext(self.snmp_engine)

        # Register GET&SET Applications at the SNMP engine for a custom SNMP context
        cmdrsp.GetCommandResponder(self.snmp_engine, snmp_context)
        cmdrsp.SetCommandResponder(self.snmp_engine, snmp_context)

        # Create a custom Management Instrumentation Controller and register it
        # as the default SNMP context controller.
        if controller is not None:
            snmp_context.contextNames[null] = controller

        return snmp_context

    def start(self):
        # Register an imaginary never-ending job to keep I/O dispatcher running forever.
        print("self.snmp_engine.transportDispatcher:", self.snmp_engine.transportDispatcher)

        self.snmp_engine.transportDispatcher.jobStarted(1)

        # Run I/O dispatcher which would receive queries and send responses.
        self.snmp_engine.transportDispatcher.runDispatcher()
        try:
            self.snmp_engine.transportDispatcher.runDispatcher()

        finally:
            self.snmp_engine.transportDispatcher.closeDispatcher()

    def start_background(self):
        t = threading.Thread(target=self.start)
        t.setDaemon(True)
        t.start()

    def stop(self):
        self.snmp_engine.transportDispatcher.closeDispatcher()


class MockedGenericMibController(instrum.AbstractMibInstrumController):
    """
    A generic SNMP Management Instrumentation Controller.

    It supports only GET requests and always echos request var-binds in response.
    """

    # Map Python types to MIB V2C types.
    V2C_TYPEMAP = {
        int: v2c.Integer,
        str: v2c.OctetString,
    }

    def __init__(self):
        self.readers: t.Dict[str, t.Union[str, int, t.Callable]] = {}
        self.configure()

    def configure(self):
        pass

    def register_read(self, oid: str, response: t.Union[str, int, t.Callable]):
        self.readers[oid] = response

    def readVars(self, varBinds, acInfo=(None, None)):
        for var in varBinds:
            oid = str(var[0])

            if oid not in self.readers:
                yield self.handle_error(oid, f"ERROR: OID {oid} not supported")
                continue

            try:
                response_value = self.readers[oid]
            except KeyError:
                yield self.handle_error(oid, f"ERROR: No response value for OID {oid} found")
                continue

            try:
                if callable(response_value):
                    response_value = response_value(oid=oid)
            except Exception:
                yield self.handle_error(oid, f"ERROR: Running callback for OID {oid} failed")
                continue

            try:
                v2c_type = self.V2C_TYPEMAP[type(response_value)]
            except KeyError:
                yield self.handle_error(oid, f"ERROR: Resolving type for {oid} failed: {type(response_value)}")
                continue

            try:
                snmp_response = (oid, v2c_type(response_value))
            except KeyError:
                yield self.handle_error(oid, f"ERROR: Creating response with oid={oid}, value={response_value} failed")
                continue

            msg = f"INFO:  Response value for OID {oid} is {response_value}"
            self.log(msg)
            yield snmp_response

    def handle_error(self, oid: str, message: str):
        self.log(message)
        return oid, v2c.OctetString(message)

    @staticmethod
    def log(*msg):
        print(*msg, file=sys.stderr)


class SynologyDiskStationMib(Enum):
    """
    An enumeration of all MIB OIDs used by Synology DiskStation.
    """

    LOAD01 = "1.3.6.1.4.1.2021.10.1.5.1"
    LOAD05 = "1.3.6.1.4.1.2021.10.1.5.2"
    LOAD15 = "1.3.6.1.4.1.2021.10.1.5.3"


class MockedSynologyMibController(MockedGenericMibController):
    """
    An SNMP Management Instrumentation Controller mocking a Synology DiskStation.
    """

    def configure(self):
        self.register_read(oid=SynologyDiskStationMib.LOAD01.value, response=int(13.42 * 100))
        self.register_read(oid=SynologyDiskStationMib.LOAD05.value, response=int(8.13 * 100))
        self.register_read(oid=SynologyDiskStationMib.LOAD15.value, response=int(5.33 * 100))


def main():

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
    snmpd.start()
    snmpd.stop()


if __name__ == "__main__":
    main()
