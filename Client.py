import sys
import Ice

Ice.loadSlice('bank.ice')
import Bank

port = 10000


def login(pesel):
    try:

        account_base = communicator.stringToProxy(
            "premium/" + pesel + ":tcp -h localhost -p " + str(port) + ":udp -h localhost -p " + str(port))
        account = Bank.PremiumAccountPrx.checkedCast(account_base)
    except:
        account_base = communicator.stringToProxy(
            "standard/" + pesel + ":tcp -h localhost -p " + str(port) + ":udp -h localhost -p " + str(port))
        account = Bank.AccountPrx.checkedCast(account_base)
    print("successfully logged in as " + account_type(account) + "/" + pesel)
    return account


def account_type(account):
    if isinstance(account, Bank.PremiumAccountPrx):
        return "premium"
    return "standard"


def new_account(param, account_factory):
    name = param[0]
    surname = param[1]
    pesel = param[2]
    income = float(param[3])

    account_factory.crete(Bank.Person(name, surname, pesel), income)
    return login(pesel)


def setPeriod(param):
    currency_type = param[0]
    cost = float(param[1])
    p = input("write start date of your loan like January 2, 2010")
    start = p
    p = input("write end date of your loan like January 2, 2010")
    end = p

    return Bank.Credit(start, end, Bank.Cost(currencyToEnum(currency_type), cost))


def currencyToEnum(cur):
    if cur == "USD":
        return Bank.CurrencyType.USD
    elif cur == "EUR":
        return Bank.CurrencyType.EUR
    elif cur == "CAD":
        return Bank.CurrencyType.CAD
    elif cur == "GBP":
        return Bank.CurrencyType.GBP
    else:
        raise ValueError


with Ice.initialize(sys.argv) as communicator:
    base = communicator.stringToProxy(
        "factory/servant1:tcp -h localhost -p " + str(port) + ":udp -h localhost -p " + str(port))
    account_factory = Bank.AccountFactoryPrx.checkedCast(base)

    l = ""
    account = None

    while l != "quit":
        try:
            l = input("what do you want to do?\n")
            if l.startswith("login"):
                account = login(l.split(" ")[1])
            elif l == "type":
                print(account_type(account))
            elif l.startswith("new"):
                account = new_account(l.split(" ")[1:], account_factory)
            elif l.startswith("balance"):
                print(str(account.getBalance()))
            elif l.startswith("transfer"):
                account.transfer(float(l.split(" ")[1]))
            elif l.startswith("loan"):
                if account_type(account) == "standard":
                    print("you cannot take a loan. You are too poor!")
                else:
                    cost = account.askForLoan(setPeriod(l.split(" ")[1:]))
                    print(cost)
        except ValueError:
            print("you pass wrong value")
        except Bank.UnsupportedCurrencyException:
            print("you bank do not have this currency")
        except Ice.ObjectNotExistException:
            print("such object does not exist")
        except AttributeError:
            print("you cannot transfer without account ")
        except Bank.DateFormatException:
            print(" you pass date in wrong format")
        # except:
        #     print("unknown error.try again")
