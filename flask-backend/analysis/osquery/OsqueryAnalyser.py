import constants
from analysis import SecurityIssueTypes
from analysis.Recommendation import Recommendation
from analysis.SecurityIssue import SecurityIssue
from handler.DatabaseHandler import DatabaseHandler
from handler.HostInformation import HostInformation


# Analysis class for osquery security issues. Osquery needs to be installed on check host.
class OsqueryAnalyser:
    def __init__(self, configuration):
        self.configuration = configuration
        self.database_handler = DatabaseHandler(constants.MONGO_URI).mongo[constants.PI_DATABASE_NAME][constants.OSQUERY_AND_COLLECTION_NAME_USB_DEVICES]

    # check for unknown connected usb devices to a host.
    def check_connected_usb_devices(self, host: HostInformation):
        # get distinct serial numbers of usb devices from the past from database to identify
        distinct_usb_serials = self.database_handler.distinct('columns.serial', {'host_ip': host.ip})

        # find last status of usb devices
        connected_usbs = []
        for serial in distinct_usb_serials:
            entries = self.database_handler.find({'host_ip': host.ip, 'columns.serial': serial})\
                .sort('unixTime', -1).limit(1)

            for entry in entries:
                # check if usb stick was added (= connected)
                if entry.get('action') == 'added':
                    connected_usbs.append(entry)
                break

        # check for secrity issues
        unknown_usbs = self.compare_connected_usbs_with_configuration(connected_usbs)

        # check if empty
        if unknown_usbs:
            # description building
            usbs_display = ', '.join([usb["columns"]["model"] for usb in connected_usbs if usb["columns"]["model"] is not None])
            description = 'Connected USB(s): ' + usbs_display + '. Found unknown USB(s): '
            unknown_usbs_display = ', '.join([usb["columns"]["model"] for usb in unknown_usbs if usb["columns"]["model"] is not None])

            description += unknown_usbs_display

            # build recommendation
            recommendation = Recommendation(constants.OSQUERY,
                                            description,
                                            'Disconnect unknown USB(s): ' + unknown_usbs_display)
            return SecurityIssue(SecurityIssueTypes.OSQUERY_CONNECTED_USBS,
                                 recommendation,
                                 False)
        else:
            # no security issues found
            print('Unknown USB check on ' + host.ip + ': Found ' + str(connected_usbs) + '! STATUS OK')
            return None

    # Search for usb device differences with the configuration
    def compare_connected_usbs_with_configuration(self, connected_usbs):
        # get allowlisted usb devices
        allowlisted = self.configuration['allow_list_usbs'].split("\n")
        allowlisted = [usb_name.strip() for usb_name in allowlisted]

        # check if in allowlist
        not_allowlisted = []
        for usb in connected_usbs:
            if not usb["columns"]["model"] in allowlisted:
                not_allowlisted.append(usb)

        return not_allowlisted
