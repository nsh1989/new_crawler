from zeep import Client, exceptions


class DAT:

    Ecode_wsdl = 'https://www.datgroup.com/DATECodeSelection/services/VehicleIdentificationService?wsdl'
    header = {}
    token = None
    sessionID = None

    @staticmethod
    def getToken(customerNumber, customerLogin, customerPassword, interfacePartnerNumber,
                 interfacePartnerSignature) -> str:
        token_wsdl = 'https://www.dat.de/DATECodeSelection/services/Authentication?wsdl'
        token_param = {
            'request': {
                'customerNumber': customerNumber,
                'customerLogin': customerLogin,
                'customerPassword': customerPassword,
                'interfacePartnerNumber': interfacePartnerNumber,
                'interfacePartnerSignature': interfacePartnerSignature
            }
        }
        client = Client(wsdl=token_wsdl)
        return client.service.generateToken(**token_param)

    def MakeHttpHeader(self, token):
        header = {
            'DAT-AuthorizationToken': token,
            # 'Content-Type': 'content="text/html; charset=UTF-8',
            # 'accept-language': 'ko,en-US;q=0.9,en;q=0.8,ja;q=0.7,ru;q=0.6,kk;q=0.5'
        }

        self.header = header

    @staticmethod
    def MakeSessionID(customerNumber, customerLogin, interfacePartnerNumber, interfacePartnerSignature,
                      customerSignature) -> str:

        token_wsdl = 'https://www.dat.de/DATECodeSelection/services/Authentication?wsdl'
        client = Client(wsdl=token_wsdl)
        login_data = {
            'request': {
                'customerNumber': customerNumber,
                'customerLogin': customerLogin,
                'customerSignature': customerSignature,
                'interfacePartnerNumber': interfacePartnerNumber,
                'interfacePartnerSignature': interfacePartnerSignature,
                # 'productVariant': 'etn'
            }
        }
        return client.service.doLogin(**login_data)

    def __init__(self):
        self.getToken('1332560', 'parkwonb', 'parkwonb01', '1332560',
                      '268F665F1D8C348E98479B3C323839158F9B48D45EACE60426A4AFC68FA562F6')
        self.MakeHttpHeader(self.token)
        self.MakeSessionID('1332560', 'parkwonb', '1332560',
                           '268F665F1D8C348E98479B3C323839158F9B48D45EACE60426A4AFC68FA562F6',
                           'FB9457B9BF60CEB375E18469EFD76519CEFD82ACCEC1E235611947ECB0C34EE5')

    def getEcodeByVin(self, vin):
        ecode = None
        client = Client(wsdl=self.Ecode_wsdl)
        client.transport.session.headers.update(self.header)
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
                'sessionID': self.sessionID
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
