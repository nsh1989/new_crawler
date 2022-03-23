from zeep import Client, exceptions


class DAT:
    # Ecode_wsdl = 'https://www.datgroup.com/DATECodeSelection/services/VehicleIdentificationService?wsdl'
    # header = {}
    # token = None
    # sessionID = None

    @staticmethod
    def get_token(customer_number, customer_login, customer_password, interface_partner_number,
                  interface_partner_signature) -> str:
        token_wsdl = 'https://www.dat.de/DATECodeSelection/services/Authentication?wsdl'
        token_param = {
            'request': {
                'customerNumber': customer_number,
                'customerLogin': customer_login,
                'customerPassword': customer_password,
                'interfacePartnerNumber': interface_partner_number,
                'interfacePartnerSignature': interface_partner_signature
            }
        }
        client = Client(wsdl=token_wsdl)
        return client.service.generateToken(**token_param)

    @staticmethod
    def make_http_header(token) -> dict:
        header = {
            'DAT-AuthorizationToken': token,
            # 'Content-Type': 'content="text/html; charset=UTF-8',
            # 'accept-language': 'ko,en-US;q=0.9,en;q=0.8,ja;q=0.7,ru;q=0.6,kk;q=0.5'
        }

        return header

    @staticmethod
    def make_session_id(customer_number, customer_login, interface_partner_number, interface_partner_signature,
                        customer_signature) -> str:

        token_wsdl = 'https://www.dat.de/DATECodeSelection/services/Authentication?wsdl'
        client = Client(wsdl=token_wsdl)
        login_data = {
            'request': {
                'customerNumber': customer_number,
                'customerLogin': customer_login,
                'customerSignature': customer_signature,
                'interfacePartnerNumber': interface_partner_number,
                'interfacePartnerSignature': interface_partner_signature,
                # 'productVariant': 'etn'
            }
        }
        return client.service.doLogin(**login_data)

    def __init__(self):
        self.get_token('1332560', 'parkwonb', 'parkwonb01', '1332560',
                       '268F665F1D8C348E98479B3C323839158F9B48D45EACE60426A4AFC68FA562F6')
        self.make_http_header(self.token)
        self.make_session_id('1332560', 'parkwonb', '1332560',
                             '268F665F1D8C348E98479B3C323839158F9B48D45EACE60426A4AFC68FA562F6',
                             'FB9457B9BF60CEB375E18469EFD76519CEFD82ACCEC1E235611947ECB0C34EE5')

    @staticmethod
    def get_ecode_by_vin(vin, header: dict, session_id: str) -> str:
        ecode_wsdl = 'https://www.datgroup.com/DATECodeSelection/services/VehicleIdentificationService?wsdl'
        ecode: str
        client = Client(wsdl=ecode_wsdl)
        client.transport.session.headers.update(header)
        # vin = 'VSSDATTESTSTUB002'
        req = {
            'request': {
                'restriction': 'ALL',
                'vin': vin,
                'coverage': 'ALL',
                'locale': {
                    'country': 'de',
                    'datCountryIndicator': 'de',
                    'language': 'de'
                },
                'sessionID': session_id
            }
        }
        try:
            resp = client.service.getVehicleIdentificationByVin(**req)
            ecode = resp['Dossier'][0]['Vehicle']['DatECode']['_value_1']
            print(f"datAPI getEcodeByVin {ecode} found ")
        except exceptions.Fault as f:
            print(f)
            return None
        except exceptions.Error as e:
            print(e)
            return None

        return ecode
