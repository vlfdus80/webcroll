# -*-coding: utf-8 -*-

import win32com.client
import pythoncom
import os, sys
import inspect
import sqlite3
import pandas as pd
from pandas import DataFrame, Series, Panel
import psycopg2
import pythoncom
from django.http import HttpResponse


class XASessionEvents:
    상태 = False

    def OnLogin(self, code, msg):
        print("OnLogin : ", code, msg)
        XASessionEvents.상태 = True

    def OnLogout(self):
        pass

    def OnDisconnect(self):
        pass


class XAQueryEvents:
    상태 = False

    def OnReceiveData(self, szTrCode):
        print("OnReceiveData : %s" % szTrCode)
        XAQueryEvents.상태 = True

    def OnReceiveMessage(self, systemError, messageCode, message):
        print("OnReceiveMessage : ", systemError, messageCode, message)



def Login(url='demo.ebestsec.co.kr', port=200001, svrtype=0, id='XXX', pwd='XXX', cert='XXX'):
    session = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
    session.SetMode("_XINGAPI7_", "TRUE")
    result = session.ConnectServer(url, port)

    if not result:
        nErrCode = session.GetLastError()
        strErrMsg = session.GetErrorMessage(nErrCode)
        return (False, nErrCode, strErrMsg, None, session)

    session.Login(id, pwd, cert, svrtype, 0)

    while XASessionEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    계좌 = []
    계좌수 = session.GetAccountListCount()

    for i in range(계좌수):
        계좌.append(session.GetAccountList(i))

    return (True, 0, "OK", 계좌, session)




def t1305(단축코드='', 일주월구분='1', 날짜='', IDX='', 건수='900'):
    '''
    기간별주가
    '''
    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
    pathname = os.path.dirname(sys.argv[0])

    MYNAME = inspect.currentframe().f_code.co_name
    INBLOCK = "%sInBlock" % MYNAME
    OUTBLOCK = "%sOutBlock" % MYNAME
    OUTBLOCK1 = "%sOutBlock1" % MYNAME
    RESFILE = "C:\\eBEST\\xingAPI\\Res\\t1305.res"

    query.LoadFromResFile(RESFILE)
    query.SetFieldData(INBLOCK, "shcode", 0, 단축코드)
    query.SetFieldData(INBLOCK, "dwmcode", 0, 일주월구분)
    query.SetFieldData(INBLOCK, "date", 0, 날짜)
    query.SetFieldData(INBLOCK, "idx", 0, IDX)
    query.SetFieldData(INBLOCK, "cnt", 0, 건수)
    query.Request(0)

    while XAQueryEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    result = []
    nCount = query.GetBlockCount(OUTBLOCK)
    for i in range(nCount):
        CNT = int(query.GetFieldData(OUTBLOCK, "cnt", i).strip())
        날짜 = query.GetFieldData(OUTBLOCK, "date", i).strip()
        IDX = int(query.GetFieldData(OUTBLOCK, "idx", i).strip())

        lst = [CNT, 날짜, IDX]
        result.append(lst)

    df = DataFrame(data=result, columns=['CNT', '날짜', 'IDX'])

    result = []
    nCount = query.GetBlockCount(OUTBLOCK1)
    """       
    날짜 dates,
    시가 open,
    고가 high,
    저가 low,
    종가 close,
    전일대비구분 sign,
    전일대비 change,
    등락율 diff,
    누적거래량 volume,
    거래증가율 diff_vol,
    체결강도 chdegree,
    소진율 sojinrate,
    회전율 changerate,
    외인순매수 fpvolume,
    기관순매수 covolume,
    종목코드 shcode,
    누적거래대금 valueamount,
    개인순매수 ppvolume,
    시가대비구분 o_sign,
    시가대비 o_change,
    시가기준등락율 o_diff,
    고가대비구분 h_sign,
    고가대비 h_change,
    고가기준등락율 h_diff,
    저가대비구분 l_sign,
    저가대비 l_change,
    저가기준등락율 l_diff,
    시가총액 marketcap """
    for i in range(nCount):
        dates = query.GetFieldData(OUTBLOCK1, "date", i).strip()
        openp = int(query.GetFieldData(OUTBLOCK1, "open", i).strip())
        highp = int(query.GetFieldData(OUTBLOCK1, "high", i).strip())
        lowp = int(query.GetFieldData(OUTBLOCK1, "low", i).strip())
        closep = int(query.GetFieldData(OUTBLOCK1, "close", i).strip())
        sign = query.GetFieldData(OUTBLOCK1, "sign", i).strip()
        change = int(query.GetFieldData(OUTBLOCK1, "change", i).strip())
        diff = float(query.GetFieldData(OUTBLOCK1, "diff", i).strip())
        volume = int(query.GetFieldData(OUTBLOCK1, "volume", i).strip())
        diff_vol = float(query.GetFieldData(OUTBLOCK1, "diff_vol", i).strip())
        chdegree = float(query.GetFieldData(OUTBLOCK1, "chdegree", i).strip())
        sojinrate = float(query.GetFieldData(OUTBLOCK1, "sojinrate", i).strip())
        changerate = float(query.GetFieldData(OUTBLOCK1, "changerate", i).strip())
        fpvolume = int(query.GetFieldData(OUTBLOCK1, "fpvolume", i).strip())
        covolume = int(query.GetFieldData(OUTBLOCK1, "covolume", i).strip())
        shcode = query.GetFieldData(OUTBLOCK1, "shcode", i).strip()
        valueamount = int(query.GetFieldData(OUTBLOCK1, "value", i).strip())
        ppvolume = int(query.GetFieldData(OUTBLOCK1, "ppvolume", i).strip())
        o_sign = query.GetFieldData(OUTBLOCK1, "o_sign", i).strip()
        o_change = int(query.GetFieldData(OUTBLOCK1, "o_change", i).strip())
        o_diff = float(query.GetFieldData(OUTBLOCK1, "o_diff", i).strip())
        h_sign = query.GetFieldData(OUTBLOCK1, "h_sign", i).strip()
        h_change = int(query.GetFieldData(OUTBLOCK1, "h_change", i).strip())
        h_diff = float(query.GetFieldData(OUTBLOCK1, "h_diff", i).strip())
        l_sign = query.GetFieldData(OUTBLOCK1, "l_sign", i).strip()
        l_change = int(query.GetFieldData(OUTBLOCK1, "l_change", i).strip())
        l_diff = float(query.GetFieldData(OUTBLOCK1, "l_diff", i).strip())
        marketcap = int(query.GetFieldData(OUTBLOCK1, "marketcap", i).strip())

        lst = [dates, openp, highp, lowp, closep, sign, change, diff, volume, diff_vol, chdegree, sojinrate, changerate, fpvolume, covolume, shcode, valueamount, ppvolume,
               o_sign, o_change, o_diff, h_sign, h_change, h_diff, l_sign, l_change, l_diff, marketcap]
        result.append(lst)

    df1 = DataFrame(data=result,
                    columns=['dates', 'openp', 'highp', 'lowp', 'closep', 'sign', 'change', 'diff', 'volume', 'diff_vol', 'chdegree', 'sojinrate',
                             'changerate', 'fpvolume', 'covolume', 'shcode', 'valueamount', 'ppvolume', 'o_sign', 'o_change', 'o_diff', 'h_sign',
                             'h_change', 'h_diff', 'l_sign', 'l_change', 'l_diff', 'marketcap'])

    XAQueryEvents.상태 = False
    # print(df1)
    con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
    selectsql = ''' select shcode,closep from periodprice where shcode=%s and dates=to_date(%s,'YYYYMMDD')'''
    sql = ''' insert into periodprice values(nextval('periodprice_id_seq'),to_date(%s,'YYYYMMDD'),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '''
    cur = con.cursor()

    for i in range(len(df1.index)):
        cur.execute(selectsql,(str(df1.loc[i][15]),str(df1.loc[i][0])))
        rows = cur.fetchall()
        if(len(rows)<1):
            cur.execute(sql, (str(df1.loc[i][0]),int(df1.loc[i][1]),int(df1.loc[i][2]),int(df1.loc[i][3]),int(df1.loc[i][4]),int(df1.loc[i][5]),int(df1.loc[i][6]),float(df1.loc[i][7]),int(df1.loc[i][8]),float(df1.loc[i][9]),float(df1.loc[i][10]),float(df1.loc[i][11]),float(df1.loc[i][12]),int(df1.loc[i][13]),int(df1.loc[i][14]),str(df1.loc[i][15]),int(df1.loc[i][16]),int(df1.loc[i][17]),int(df1.loc[i][18]),int(df1.loc[i][19]),float(df1.loc[i][20]),int(df1.loc[i][21]),int(df1.loc[i][22]),float(df1.loc[i][23]),int(df1.loc[i][24]),int(df1.loc[i][25]),float(df1.loc[i][26]),int(df1.loc[i][27])))
            cur.execute('commit;')
    print(str(df1.loc[i][15]))
    cur.close()
    con.close()
    return (df, df1)


def updateperiodprice(request):
    pythoncom.CoInitialize()
    result, code, msg, 계좌, session = Login(url='hts.ebestsec.co.kr', port=200001, svrtype=0, id='vlfdus80', pwd='!a571132', cert='!!a5711327')

    print("111")
    con = psycopg2.connect("dbname='webcrolldb' user='postgres' host='localhost' password='1111'")
    print("222")
    selectsql = " select code from company where code not in (select code from company limit 232); "
    print("333")
    cur = con.cursor()
    print("444")
    cur.execute(selectsql)
    print("555")
    rows = cur.fetchall()
    print("666")
    for row in rows:
        print("777")
        company_code = row[0]
        df0, df = t1305(단축코드=company_code, 일주월구분='1', 날짜='', IDX='', 건수='5000')
        print("888")
    cur.close()
    con.close()

    return HttpResponse('ok')
