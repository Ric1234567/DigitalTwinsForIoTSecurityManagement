import constants
from analysis import SecurityIssueTypes
from analysis.Recommendation import Recommendation
from analysis.SecurityIssue import SecurityIssue
from handler.DatabaseHandler import DatabaseHandler
from handler.HostInformation import HostInformation


class OsqueryAnalyser:
    def __init__(self, configuration):
        self.configuration = configuration

    def check_connected_usb_devices(self, host: HostInformation):
        print('Checking connected usb devices...')

        # get from database
        database_handler = DatabaseHandler(constants.MONGO_URI)
        distinct_usb_serials = database_handler.mongo[constants.PI_DATABASE_NAME][constants.OSQUERY_AND_COLLECTION_NAME_USB_DEVICES]\
            .distinct('columns.serial', {'host_ip': host.ip})

        connected_usbs = []
        for serial in distinct_usb_serials:
            entries = database_handler.mongo[constants.PI_DATABASE_NAME][constants.OSQUERY_AND_COLLECTION_NAME_USB_DEVICES]\
                .find({'host_ip': host.ip, 'columns.serial': serial})\
                .sort('unixTime', -1).limit(1)

            for entry in entries:
                # check if usb stick was added (= connected)
                if entry.get('action') == 'added':
                    connected_usbs.append(entry)
                break

        not_whitelisted_usbs = self.compare_with_configuration(connected_usbs)

        # check if empty
        if not_whitelisted_usbs:
            # description building
            usbs_display = ''
            for usb in connected_usbs:
                model = usb["columns"]["model"]
                if model is not None:
                    usbs_display += model + ', '

            description = 'Connected USB(s): ' + usbs_display + '. Found unknown USB(s): '
            unknown_usbs_display = ''
            for usb in not_whitelisted_usbs:
                model = usb["columns"]["model"]
                if model is not None:
                    unknown_usbs_display += model + ', '

            description += unknown_usbs_display

            recommendation = Recommendation(constants.OSQUERY,
                                            description,
                                            'Disconnect unknown USB(s): ' + unknown_usbs_display)
            return SecurityIssue(SecurityIssueTypes.OSQUERY_CONNECTED_USBS,
                                 host,
                                 recommendation,
                                 False)
        else:
            print('USB Check: OK')
            return None

    def compare_with_configuration(self, connected_usbs):
        whitelisted = self.configuration['whitelist_usbs'].split("\n")
        whitelisted = [usb_name.strip() for usb_name in whitelisted]
        
        not_whitelisted = []
        for usb in connected_usbs:
            if not usb["columns"]["model"] in whitelisted:
                not_whitelisted.append(usb)

        return not_whitelisted
