from DB import Database as DB

class AssetforTest():
    # static variables
    btc_balance = 0
    krw_balance = 10000000
    btc_avg_price = 0
    current_btc_price = 0
    trade_fee = 0.0005

    @classmethod
    def initializeAsset(cls):
        if DB.isExist("asset") and DB.isExist("recommendation"):
            # load asset info
            print("Load previous asset information.")
            btc_balance, krw_balance, btc_avg_price, current_btc_price = DB.loadLastAsset()
            decision, ratio = DB.loadLastRecommendation()

            cls.btc_balance = btc_balance
            cls.krw_balance = krw_balance
            cls.btc_avg_price = btc_avg_price
            cls.current_btc_price = current_btc_price

            if decision == "buy":
                cls.executeBuy(ratio)
            elif decision == "sell":
                cls.executeSell(ratio)

        else:
            # initialize asset info
            print("There is no previous information. Initializing...")
            cls.btc_balance = 0
            cls.krw_balance = 10000000
            cls.btc_avg_price = 0
            cls.current_btc_price = 0

            # initialize DB
            DB.dropAllTable()
            DB.createTables()
        
        cls.trade_fee = 0.0005

        return

    @classmethod
    def setBTCPrice(cls, price):
        cls.current_btc_price = price

        return

    @classmethod
    def getBalances(cls):
        balances = [{'currency': "KRW", 'balance': cls.krw_balance},
        {'currency': "BTC", 'balance': cls.btc_balance,'avg_buy_price': cls.btc_avg_price}]

        return balances

    @classmethod
    def printResult(cls, action):
        total_asset = round(cls.krw_balance + cls.btc_balance * cls.current_btc_price)
        
        print("="*100)
        print(f"{action} BTC, the result is...")
        print(f"BTC average price: {cls.btc_avg_price}")
        print(f"BTC balance: {cls.btc_balance}")
        print(f"KRW balance: {cls.krw_balance}")
        print(f"total asset: {total_asset}")
        print("="*100+"\n")

        return

    @classmethod
    def executeBuy(cls, ratio):
        if ratio >= (1-cls.trade_fee):
            buy_amount = cls.krw_balance * (1-cls.trade_fee)
            cls.krw_balance = 0
        else:
            buy_amount = cls.krw_balance * ratio
            cls.krw_balance -= buy_amount * (1 + cls.trade_fee)
        past_btc_balance = cls.btc_balance
        cls.btc_balance += buy_amount / cls.current_btc_price
        cls.btc_avg_price = round((buy_amount + past_btc_balance * cls.btc_avg_price) / cls.btc_balance)

        cls.printResult('bought')

        return

    @classmethod
    def executeSell(cls, ratio):
        sell_amount = cls.btc_balance * ratio
        cls.btc_balance -= sell_amount
        cls.krw_balance += (sell_amount * cls.current_btc_price) * (1 - cls.trade_fee)
        if cls.btc_balance == 0: 
            cls.btc_avg_price = 0

        cls.printResult('sold')

        return

    @classmethod
    def executeHold(cls):
        cls.printResult('hold')

        return