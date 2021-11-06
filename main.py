import csv
import MySQLdb.cursors, math
from flask import Flask, render_template, request, redirect, flash, session, url_for,session
from flask_mysqldb import MySQL
from decimal import Decimal
from datetime import timedelta
import os.path
from binance.client import Client

client = Client("HO1sCsC1Pd1tBaV45Fz3KJSjeAzWNu985G64DQG0xqW9fGzIBInVrqE7NJcATln7","1teSu8d6jSm3NHeDlg6ICXbE51QaS8RDZH8IVujaH6aJD8DuEfaQpSfPzgnaqFi0")


adminPassword = "word"  # admin password ask what he wants here

app = Flask(__name__)
app.secret_key = "don't tell anyone"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password8"
app.config["MYSQL_DB"] = "login"
app.permanent_session_lifetime= timedelta(hours = 2) #store session date for 5 minutes
db = MySQL(app)

coinsOwn = ['Aave', 'Bitcoin', 'Bitcoincash', 'Chainlink', 'Cosmos', 'Etherium', 'Filecoin', 'ICP', 'Nucypher',
            'Origin', 'Storj']
coinTicker = {'Aave': 'AAVE','Bitcoin': 'BTC','Bitcoincash':'BCH','Chainlink':'LINK','Cosmos':'ATOM','Etherium':'ETH','Filecoin':'FIL','ICP':'ICP','Nucypher':'NU',
              'Origin':'OGN','Storj':'STORJ'}
coinPrice=[]
nameShareInitialprice = []

picfolder = os.path.join('static','pics')
app.config['UPLOAD_FOLDER'] = picfolder


# the Post will get the data from the online form
# Get retrieves data from the sql database
#the route handels the login page
@app.route('/', methods=['GET', 'POST'])
def index():
    pic1 = os.path.join(picfolder,'logo.png')
    if (request.method == 'POST'):
        if ('Name' in request.form and 'Password' in request.form):
            na = request.form['Name']
            pa = request.form['Password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM logininfo WHERE name=%s AND password=%s", (na, pa))
            info = cursor.fetchone()
            if info is not None:
                if (info['Name'] == na and info['Password'] == pa):
                    if (na == 'ADMIN'):
                        session['loginsuccess'] = True
                        nameShareInitialprice.clear()
                        return redirect(url_for('adminOption'))
                    else:
                        session['loginsuccess'] = True
                        nameShareInitialprice.clear()
                        session["user"] = na
                        return redirect(url_for('logIn'))
                else:
                    flash("Incorrect Name or Password please try again")
                    return redirect(url_for('index'))
            else:
                flash("Incorrect Name or Password please try again")
                return redirect(url_for('index'))
    return render_template('login.html', logIMG = pic1)

data=[]
nax=[]
seHist=[] #this pah allows a user to search for any coin that exsits on binances data base
@app.route('/search', methods = ["GET","POST"])
def searchCoins():
    if "user" in session:
        pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'smalLogo.png')
        data.clear()
        nax.clear()
        proce = []
        if(request.method  == 'POST'):
            if(session['loginsuccess']==True and 'search' in request.form):
                x = False
                if("Code" in request.form):
                    a= request.form["Code"]
                    a=a.upper()
                    seHist.append(a)
                    if(a.find("USDT") >0) :
                        nax.append( a[0:1+a.find('USDT')])
                        exchange_info = client.get_symbol_ticker()
                        for s in exchange_info:
                            if(s['symbol'] == a):
                                data.clear()
                                data.append(s['price'])
                                x=True
                                l = {'symbol': a}
                                data.append((client.get_ticker(**l))['askPrice'])
                                data.append((client.get_ticker(**l))['openPrice'])
                                data.append((client.get_ticker(**l))['highPrice'])
                                data.append((client.get_ticker(**l))['lowPrice'])
                                data.append((client.get_ticker(**l))['volume'])
                        candelstick = client.get_historical_klines(a,Client.KLINE_INTERVAL_1DAY, "1 Dec, 2017")
                        for da in candelstick:
                            cand={
                                "time":(da[0]/1000),
                                "open": da[1],
                                "high": da[2],
                                "low": da[3],
                                "close": da[4]
                            }
                            proce.appends(cand)
                    else:
                        nax.append(a)
                        print('L')
                        a = a +"USDT"
                        exchange_info = client.get_symbol_ticker()
                        for s in exchange_info:
                            if(s['symbol'] == a):
                                data.clear()
                                data.append(s['price'])
                                x=True
                                l = {'symbol': a}
                                data.append((client.get_ticker(**l))['askPrice'])
                                data.append((client.get_ticker(**l))['openPrice'])
                                data.append((client.get_ticker(**l))['highPrice'])
                                data.append((client.get_ticker(**l))['lowPrice'])
                                data.append((client.get_ticker(**l))['volume'])
                        candelstick = client.get_historical_klines(a, Client.KLINE_INTERVAL_1DAY, "1 Dec, 2017")
                        for da in candelstick:
                            cand = {
                                "time": da[0]/1000,
                                "open": da[1],
                                "high": da[2],
                                "low": da[3],
                                "close": da[4]
                            }
                            proce.append(cand)
                    if(x == False):
                        flash("redo")
                        return redirect(url_for('searchCoins'))
            if ('add' in request.form):
                b = request.form['add']
                if (b == 'Add to Watch List' and seHist):
                    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("SELECT * FROM `watchlist` WHERE `Name`=%s", [session["user"]])
                    info = cursor.fetchone()
                    if(info['watch']):
                        info = info['watch']+','+ seHist[-1]
                    else:
                        info = seHist[-1]
                    cursor.execute("""UPDATE watchlist SET """ +'watch' + """ = %s WHERE Name = %s""", (info, session["user"]))
                    db.connection.commit()
                    searchedCoin =''
                    seHist.clear();
        return render_template('SearchCoins.html', have= data, nam = nax, pic = pic1, lineGraph = proce)
    else:
        return redirect(url_for('index'))

@app.route('/logIn')
def logIn():
    if "user" in session:
        pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'smalLogo.png')
        coinNames = []
        initialInvestment = []
        cash=''
        if(session['loginsuccess']==True):
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM `cash` WHERE `Name`=%s", [session["user"]])
            info = cursor.fetchone()
            print(info)
            cash = info['liquidCash']
            nameShareInitialprice.clear()
            if(len(nameShareInitialprice) == 0):
                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM `crypto` WHERE `Name`=%s", [session["user"]])
                info = cursor.fetchone()
                coinList = coinsOwn[:]
                for name in coinList:
                    prices = info[name]
                    if(prices != '0' and prices is not None):
                        coinNames.append(name)
                        markValue = ((client.get_symbol_ticker(symbol=(coinTicker[name]+"USDT")))['price'])
                        tot = prices.split(',')
                        tot.pop()
                        avgPrice = 0.00
                        initialInvestmentPerCoin =0
                        div = 1
                        for price in tot:
                            coinPrice.append(markValue)
                            x = price.split(':')
                            nameShareInitialprice.append(name+":"+x[1]+":"+x[0]+",")
                            initialInvestmentPerCoin = initialInvestmentPerCoin+(float(x[0]) * float(x[1]))

                        initialInvestment.append(initialInvestmentPerCoin)
        return render_template('CurrentFormat.html',cashHeld =cash, pic = pic1, have= nameShareInitialprice, compare = coinPrice, coins = coinNames, piePriceData=initialInvestment)
    else:
        return redirect(url_for('index'))
#Allows admin to acces any of the user profiles
@app.route('/Master_Account')
def allAccounts():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'smalLogo.png')
    coinNames = []
    initialInvestment = []

    if(session['loginsuccess']==True):

        if(len(nameShareInitialprice) == 0):
            coinList = coinsOwn[:]
            for name in coinList:
                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT "+name+" FROM crypto ")
                info = cursor.fetchall()
                for x in info:

                    prices = x[name]
                    if(prices != '0' and prices is not None):
                        coinNames.append(name)
                        markValue = ((client.get_symbol_ticker(symbol=(coinTicker[name]+"USDT")))['price'])
                        tot = prices.split(',')
                        tot.pop()
                        avgPrice = 0.00
                        initialInvestmentPerCoin =0
                        div = 1
                        for price in tot:
                            coinPrice.append(markValue)
                            x = price.split(':')
                            nameShareInitialprice.append(name+":"+x[1]+":"+x[0]+",")
                            initialInvestmentPerCoin = initialInvestmentPerCoin+(float(x[0]) * float(x[1]))

                        initialInvestment.append(initialInvestmentPerCoin)



    return render_template('CurrentFormat.html',pic = pic1, have= nameShareInitialprice, compare = coinPrice, coins = coinNames, piePriceData=initialInvestment)
#Allows users to edit their personal watchlist
@app.route('/Users/Edit_Watchlist', methods=['GET', 'POST'])
def usereditWatch():
    if "user" in session:
        pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'smalLogo.png')
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM `watchlist` WHERE `Name`=%s", [session["user"]])
        info = cursor.fetchone()
        vWatch = info["watch"].split(",")
        if (request.method == 'POST'):
            if (session['loginsuccess'] == True):
                newWatchList=[]
                if ('Remove' in request.form):
                    x = request.form['Remove']
                    print(x)
                    x=x.split(',')
                    for coinInWatchlist in vWatch:
                        remover = True
                        for coinsToRemove in x:
                            if coinInWatchlist.upper() == coinsToRemove.upper():
                                remover = False
                        if remover:
                            newWatchList.append(coinInWatchlist)
                    done = ','.join(newWatchList)
                    print(done)
                    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("""UPDATE watchlist SET """ + "watch" + """ = %s WHERE Name = %s""",
                                   (done, session["user"]))
                    db.connection.commit()
                if (request.form['Add'] != ''):
                    x = request.form['Add']
                    x=x.split(',')

                    for c in x:
                        vWatch.append(c)
                    done = ','.join(vWatch)


                    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute("""UPDATE watchlist SET """ + "watch" + """ = %s WHERE Name = %s""",
                                   (done, session["user"]))
                    db.connection.commit()
                return redirect(url_for('watchlist'))
        return render_template('userEditWatch.html',pic = pic1, list=vWatch)
    else:
        return redirect(url_for('index'))
#Allows user to access the order history route that shows them oopen buy orders and closed buy orders
@app.route('/Order_History', methods=['GET', 'POST'])
def orders():
    if "user" in session:
        pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'smalLogo.png')
        currentOrders =[]
        pastOrders =[]
        name = session["user"]
        if (session['loginsuccess'] == True):
            f = open("current.csv", "r")
            reader = csv.reader(f, delimiter=",")
            for i in reader:
                if i[0] == name:
                    currentOrders.append(i)
            f.close()
            f= open("Past.csv", "r")
            reader = csv.reader(f, delimiter=",")
            for i in reader:
                print(i)
                if i[0] == name:
                    pastOrders.append(i)

            f.close()
        return render_template('orderHist.html', current=currentOrders, past=pastOrders,pic = pic1)
    else:
        return redirect(url_for('index'))
#This route takes user to the watch list page where it shows them their current watchlist and veludi top 10 suggested
@app.route('/WatchList', methods=['GET', 'POST'])
def watchlist():
    if "user" in session:
        watchl = []
        veludiWatchl=[]
        pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'smalLogo.png')
        if (session['loginsuccess'] == True):
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM `watchlist` WHERE `Name`=%s", [session["user"]])
            info = cursor.fetchone()
            if (info and info['watch']):
                if (len(watchl) != len((info['watch']).split(','))):
                    watchl = (info['watch']).split(',')
                    count = 0;
                    for x in watchl:
                        q = x + ','
                        openPrice = math.floor(
                            Decimal(client.get_ticker(symbol=(x.upper() + 'USDT'))['openPrice']) * 100) / 100
                        q = q + str(openPrice) + ','

                        lastPrice = math.floor(Decimal(client.get_ticker(symbol=x.upper() + 'USDT')['askPrice']) * 100) / 100
                        q = q + str(lastPrice) + ','
                        highPrice = math.floor(
                            Decimal(client.get_ticker(symbol=x.upper() + 'USDT')['highPrice']) * 100) / 100
                        q = q + str(highPrice) + ','
                        lowPrice = math.floor(Decimal(client.get_ticker(symbol=x.upper() + 'USDT')['lowPrice']) * 100) / 100
                        q = q + str(lowPrice)
                        watchl[count] = q
                        count = count + 1
            else:
                watchl.append('none')
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM `watchlist` WHERE `Name`=%s", ["ADMIN"])
            info = cursor.fetchone()
            if (info and info['watch']):
                if (len(veludiWatchl) != len((info['watch']).split(','))):
                    print('eher')
                    veludiWatchl = (info['watch']).split(',')
                    count = 0
                    q = ''
                    for x in veludiWatchl:
                        q = x + ','
                        openPrice = math.floor(Decimal(client.get_ticker(symbol=(x.upper() + 'USDT'))['openPrice']) * 100) / 100
                        q = q + str(openPrice) + ','
                        lastPrice = math.floor(
                            Decimal(client.get_ticker(symbol=x.upper() + 'USDT')['askPrice']) * 100) / 100
                        q = q + str(lastPrice) + ','
                        highPrice = math.floor(
                            Decimal(client.get_ticker(symbol=x.upper() + 'USDT')['highPrice']) * 100) / 100
                        q = q + str(highPrice) + ','
                        lowPrice = math.floor(Decimal(client.get_ticker(symbol=x.upper() + 'USDT')['lowPrice']) * 100) / 100
                        q = q + str(lowPrice)
                        veludiWatchl[count] = q
                        count = count + 1
                    print(veludiWatchl)
            if ('editList' in request.form):
                b = request.form['editList']
                if (b == 'Edit Watchlist'):
                    return redirect(url_for('usereditWatch'))
        return render_template('WATCHLIST.html', list=watchl, vlist=veludiWatchl,pic = pic1)
    else:
        return redirect(url_for('index'))

@app.route('/Adminastrative/Options', methods=['GET', 'POST'])
def adminOption():
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            if ('delete' in request.form):
                b = request.form['delete']
                if (b == 'Delete Account'):
                    return redirect(url_for('delAccount'))
            elif ('buyCoin' in request.form):
                c = request.form['buyCoin']
                if (c == 'Buy'):
                    return redirect(url_for('buyCoins'))
            elif ('soldCoin' in request.form):
                c = request.form['soldCoin']
                if (c == 'Sold'):
                    return redirect(url_for('sellCoins'))
            elif ('register' in request.form):
                if(request.form['register'] == "Register"):
                    return redirect(url_for('newUser'))
            elif ('addCoin' in request.form):
                if(request.form['addCoin'] == "Add a new Coin"):
                    return redirect(url_for('newCoin'))
            elif ('seClient' in request.form):
                if(request.form['seClient'] == "Search Client"):
                    return redirect(url_for('clientSearch'))
            elif ('delCoin' in request.form):
                if(request.form['delCoin'] == "Delete a Coin"):
                    return redirect(url_for('delCoin'))
            elif ('msAccount' in request.form):
                if(request.form['msAccount'] == "All coins Owned"):
                    return redirect(url_for('allAccounts'))
            elif ('rwatch' in request.form):
                if(request.form['rwatch'] == "Edit Watchlist"):
                    return redirect(url_for('editWatch'))
            elif ('pLink' in request.form):
                if(request.form['pLink'] == "Password Change Link"):
                    return redirect(url_for('pChange'))
            elif ('aCash' in request.form):
                if(request.form['aCash'] == "Account Cash"):
                    return redirect(url_for('addCash'))
            elif ('open' in request.form):
                if (request.form['open'] == "Open Order"):
                    return redirect(url_for('openOrder'))

    return render_template('adOption.html')
#Allows admin to set open orders
@app.route('/Adminastrative/Options/Open_Order', methods=['GET', 'POST'])
def openOrder():
    a = []
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Name FROM logininfo")
    allUser = cursor.fetchall()
    for x in allUser:
        a.append(x["Name"])
    a.pop(0)  #Tis drops checking admin account
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            if("cname" in request.form):
                coin = request.form["cname"] #Name of the coin trying to change value of
                for pep in a: #pep gives account names
                    if(pep in request.form and pep+"p" in request.form and request.form[pep]): #checks for where a quantity field has been filled out
                        quant = request.form[pep] #returns the quantity of the coin
                        price = request.form[pep+"p"] #returns the price of the coin
                        f = open("current.csv", "a", newline="")
                        newOrder = [pep,coin,quant,price]
                        writer = csv.writer(f)
                        writer.writerow(newOrder)
                        f.close()
            return redirect(url_for('adminOption'))

    elif request.method == 'GET':
        return render_template('upCoin1.html', names = a)
#Allows admin to add cash to user accounts
@app.route('/options/Change_Amount_of_Cash', methods=['GET', 'POST'])
def addCash():
    if (request.method == 'POST' and session['loginsuccess'] == True):
        if ('Name' in request.form ):
            na = request.form['Name']
            addAmount = request.form['addCash']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM cash WHERE name=%s", ([na]))
            info = cursor.fetchone()
            if info is not None:
                if (info['Name'] == na):
                    cash = info['liquidCash']
                    cash = float(cash)
                    cash = cash + float(addAmount)
                    cursor.execute("""UPDATE cash SET """ + "liquidCash" + """ = %s WHERE Name = %s""", (cash, na))
                    db.connection.commit()
                    return redirect(url_for("adminOption"))
                else:
                    flash("Incorrect Name or Password please try again")
                    return redirect(url_for('addCash'))
            else:
                flash("Incorrect Name or Password please try again")
                return redirect(url_for('addCash'))
    return render_template('cashChange.html')

@app.route('/Options/PasswordChange', methods=['GET', 'POST'])
def pChange():
    if (request.method == 'POST'):
        if ('Name' in request.form and 'Password' in request.form):
            na = request.form['Name']
            pa = request.form['Password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM logininfo WHERE name=%s", [na])
            info = cursor.fetchone()
            if(info is not None and na != 'ADMIN'):
                cursor.execute("""UPDATE logininfo SET """ + "Password" + """ = %s WHERE Name = %s""", (pa, na))
                db.connection.commit()
                return redirect(url_for('index'))
            else:
                flash("Incorrect Name or Password please try again")
                return redirect(url_for('pChange'))
    return render_template("PassChange.html")
#Allows admin to edit the top 10 watchlist
@app.route('/Adminastrative/Options/Remove_Watchlist', methods=['GET', 'POST'])
def editWatch():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM `watchlist` WHERE `Name`=%s", ["ADMIN"])
    info = cursor.fetchone()
    vWatch = info["watch"].split(",")
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            newWatchList=[]
            if ('Remove' in request.form):
                x = request.form['Remove']
                print(x)
                x=x.split(',')
                for coinInWatchlist in vWatch:
                    remover = True
                    for coinsToRemove in x:
                        if coinInWatchlist.upper() == coinsToRemove.upper():
                            remover = False
                    if remover:
                        newWatchList.append(coinInWatchlist)
                done = ','.join(newWatchList)
                print(done)
                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("""UPDATE watchlist SET """ + "watch" + """ = %s WHERE Name = %s""",
                               (done, "ADMIN"))
                db.connection.commit()
            if (request.form['Add'] != ''):
                x = request.form['Add']
                x = x.split(',')
                print('start')
                print(vWatch)
                print(x)
                for c in x:
                    print(c)
                    vWatch.append(c)
                done = ','.join(vWatch)
                print(done)

                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("""UPDATE watchlist SET """ + "watch" + """ = %s WHERE Name = %s""",
                               (done, "ADMIN"))
                db.connection.commit()
            return redirect(url_for('adminOption'))



    return render_template('editWatchList.html', list=vWatch)

@app.route('/Adminastrative/Options/REGISTER', methods=['GET', 'POST'])
def newUser():
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            if ('regName' in request.form and 'regPassword' in request.form):
                name = request.form['regName']
                password = request.form['regPassword']
                cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("INSERT INTO login.logininfo(Name,Password)VALUES(%s,%s)", (name, password))
                cur.execute("INSERT INTO login.crypto(Name) VALUES (%s)",([name]))
                cur.execute("INSERT INTO login.watchlist(Name) VALUES (%s)", ([name]))
                cur.execute("INSERT INTO login.cash(Name) VALUES (%s)", ([name]))
                db.connection.commit()

                return redirect(url_for('adminOption'))
            else:
                flash("Incorrect Admin password")
                return redirect(url_for('adminOption'))

    elif request.method == 'GET':
        return render_template('register.html')

@app.route('/Adminastrative/Options/Add_Coin', methods=['GET', 'POST'])
def newCoin():
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            if ('coName' in request.form and 'cTick' in request.form):
                name = request.form['coName']
                ticker = request.form['cTick']
                coinsOwn.append(name)
                coinTicker[name] = ticker
                cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("ALTER TABLE crypto ADD " + name+" VARCHAR(100) DEFAULT 0")
                db.connection.commit()

                return redirect(url_for('adminOption'))


    elif request.method == 'GET':
        return render_template('addNewCoin.html')


@app.route('/Adminastrative/Options/Del_Coin', methods=['GET', 'POST'])
def delCoin():
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            if ('coName' in request.form and 'cTick' in request.form):
                name = request.form['coName']
                ticker = request.form['cTick']
                coinsOwn.remove(name)
                coinTicker[name] = ticker
                cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cur.execute("ALTER TABLE crypto DROP Column " + name)
                db.connection.commit()

                return redirect(url_for('adminOption'))


    elif request.method == 'GET':
        return render_template('deleteCoin.html')

@app.route('/Adminastrative/Options/Delete', methods=['GET', 'POST'])
def delAccount():
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):

            if ( 'delName' in request.form):
                name = request.form['delName']
                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM logininfo WHERE name=%s", [name])
                info = cursor.fetchone()

                if info is not None:
                    print("here")
                    cursor.execute("DELETE FROM `logininfo` WHERE `Name` = %s", [name])
                    cursor.execute("DELETE FROM `crypto` WHERE `Name` = %s", [name])
                    cursor.execute("DELETE FROM `watchlist` WHERE `Name` = %s", [name])
                    cursor.execute("DELETE FROM `cash` WHERE `Name` = %s", [name])
                    db.connection.commit()

                    return redirect(url_for('adminOption'))
                else:
                    flash("name does not exsist")
                    return redirect(url_for('delAccount'))
            else:
                flash("name does not exsist")
                return redirect(url_for('delAccount'))

    elif request.method == 'GET':
        return render_template('deleteCcount.html')

@app.route('/Adminastrative/Options/Clent_Search', methods=['GET', 'POST'])
def clientSearch():
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            if ( 'delName' in request.form):
                name = request.form['delName']
                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM logininfo WHERE name=%s", [name])
                info = cursor.fetchone()
                if info is not None:
                    session["user"] =name
                    print(name)
                    return redirect(url_for('logIn'))
                else:
                    flash("name does not exist")
                    return redirect(url_for('clientSearch'))
            else:
                flash("name does not exist")
                return redirect(url_for('clientSearch'))

    elif request.method == 'GET':
        return render_template('searchClient.html')

@app.route('/Adminastrative/Options/AddCoins', methods=['GET', 'POST'])
def buyCoins():
    a = []
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Name FROM logininfo")
    allUser = cursor.fetchall()
    for x in allUser:
        a.append(x["Name"])
    a.pop(0)
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            if("cname" in request.form):
                coin = request.form["cname"] #Name of the coin trying to change value of
                for pep in a:
                    if(pep in request.form and pep+"p" in request.form and request.form[pep]): #checks for where a quantity field has been filled out
                        quant = request.form[pep]  # returns the quantity of the coin
                        price = request.form[pep + "p"]  # returns the price of the coin
                        f = open("past.csv", "a", newline="")
                        orderFulfilled = [pep, coin, quant, price]
                        writer = csv.writer(f)
                        writer.writerow(orderFulfilled)
                        f.close()
                        f= open("current.csv", "r")
                        reader = csv.reader(f, delimiter=",")
                        lines =list()
                        found = 0
                        print(pep + "," + coin.lower()+ ","  + quant+ ","  + price)
                        for i in reader:
                            print(i)

                            if found==0 and i[0] == pep and i[1].lower() == (coin.lower()) and i[2] == (quant) and i[3] == (price) :
                                found = 1
                            else:
                                lines.append(i)
                        f.close()
                        f = open("current.csv", "w", newline="")
                        writer = csv.writer(f)
                        writer.writerows(lines)
                        f.close()
                        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                        cursor.execute("SELECT * FROM `cash` WHERE `Name`=%s", [pep])
                        info = cursor.fetchone()
                        cash = info['liquidCash']
                        cash = float(cash)
                        cash = cash - float(quant)*float(price)
                        cursor.execute("""UPDATE cash SET """ + "liquidCash" + """ = %s WHERE Name = %s""", (cash, pep))
                        db.connection.commit()
                        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                        cursor.execute("SELECT "+coin+" FROM crypto WHERE Name=%s", [pep])
                        info = cursor.fetchone()
                        theCoins = info #finds in database the person and the coin and returns quantity purchased at the different prices
                        theCoins = theCoins[coin]
                        if ( theCoins.find(price) != -1 ):

                            number = theCoins[theCoins.find(price):]
                            start = number.find(':') + 1
                            end = number.find(',')
                            num =0
                            if(len(number[start:end])== num):
                                num = float(quant)
                                num = str(num)
                                fin = theCoins[0: theCoins.find(price) + start] + num + theCoins[(end + theCoins.find(price)):]
                                cursor.execute("""UPDATE crypto SET """ + coin + """ = %s WHERE Name = %s""",(fin, pep))
                                db.connection.commit()
                            else:
                                num = float(number[start:end]) + float(quant)
                                num = str(num)
                                fin = theCoins[0: theCoins.find(price) + start] + num + theCoins[(end + theCoins.find(price)):]
                                cursor.execute("""UPDATE crypto SET """ + coin + """ = %s WHERE Name = %s""",(fin, pep))
                                db.connection.commit()


                        else:
                            if(theCoins == '0'):
                                theCoins =  price + ':' + quant + ','
                                cursor.execute("""UPDATE crypto SET """ + coin + """ = %s WHERE Name = %s""",
                                               (theCoins, pep))
                                db.connection.commit()
                            else:
                                theCoins = theCoins + price + ':' + quant + ','
                                cursor.execute("""UPDATE crypto SET """ + coin + """ = %s WHERE Name = %s""",
                                               (theCoins, pep))
                                db.connection.commit()


            return redirect(url_for('adminOption'))

    elif request.method == 'GET':
        return render_template('upCoin1.html', names = a)

@app.route('/Adminastrative/Options/SellCoins', methods=['GET', 'POST'])
def sellCoins():
    a = []
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT Name FROM logininfo")
    allUser = cursor.fetchall()
    for x in allUser:
        a.append(x["Name"])
    a.pop(0)
    if (request.method == 'POST'):
        if (session['loginsuccess'] == True):
            if("cname" in request.form):
                coin = request.form["cname"] #Name of the coin trying to change value of

                for pep in a:

                    if(pep in request.form and pep+"p" in request.form and request.form[pep]): #checks for where a quantity field has been filled out
                        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                        cursor.execute("SELECT * FROM `cash` WHERE `Name`=%s", [pep])
                        info = cursor.fetchone()
                        cash = info['liquidCash']
                        cash = float(cash)
                        quant = request.form[pep]  # returns the quantity of the coin
                        price = request.form[pep + "p"]  # returns the price of the coin
                        cash = cash + float(quant) * float(price)
                        cash = str(round(cash, 2))
                        cursor.execute("""UPDATE cash SET """ + "liquidCash" + """ = %s WHERE Name = %s""", (cash, pep))
                        db.connection.commit()
                        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                        cursor.execute("SELECT "+coin+" FROM crypto WHERE Name=%s", [pep])
                        info = cursor.fetchone()
                        theCoins = info #finds in database the person and the coin and returns quantity purchased at the different prices
                        theCoins = theCoins[coin]
                        if (theCoins.find(price) != -1 ):

                            number = theCoins[theCoins.find(price):]
                            start = number.find(':') + 1
                            end = number.find(',')

                            num = float(number[start:end]) - float(quant)
                            if(num == 0):
                                num = str(num)
                                fin = theCoins[0: theCoins.find(price)]+ theCoins[(end +1):]
                                if(fin == ''):
                                    fin ='0'
                                cursor.execute("""UPDATE crypto SET """ + coin + """ = %s WHERE Name = %s""",(fin, pep))
                                db.connection.commit()
                            else:
                                num = str(num)
                                fin = theCoins[0: theCoins.find(price) + start] + num + theCoins[(end + theCoins.find(price)):]
                                cursor.execute("""UPDATE crypto SET """ + coin + """ = %s WHERE Name = %s""",
                                               (fin, pep))
                                db.connection.commit()





            return redirect(url_for('adminOption'))

    elif request.method == 'GET':
        return render_template('upCoin2.html', names = a)



if (__name__ == '__main__'):
    app.run(debug=True)
