import tabula
import dateutil
import numpy as np
import pandas as pd
from flask import Flask, request,render_template
import pickle
import xml.etree.ElementTree as ET
from datetime import datetime,timedelta

app = Flask(__name__)

#For Enquiry Field:
Cibil_Data1 = []
#For Cibil Data:
Cibil_Data2 = []
#For Accounts:
Cibil_Data3 = []
 

#This function read cibil xm file and return data:
def CIBIL(file):
    # create element tree object 
    tree = ET.parse(file) 
    # get root element 
    root = tree.getroot() 
    context = root.find('ContextData')
    
    cibil = context.getchildren()[0].find('Applicants').find('Applicant').find('DsCibilBureau')
    credit_report = cibil.find('Response').find('CibilBureauResponse').find('BureauResponseXml').find('CreditReport')
    if credit_report:
        name_segment = credit_report.findall('NameSegment')[0]
        
        try:
            id_segment = credit_report.findall('IDSegment')[0]
        except:
            id_segment = '-'
            
        try:    
            tele_segment = credit_report.findall('TelephoneSegment')[0]
        except:
            tele_segment = '-'
        
        try:
            email_segment = credit_report.findall('EmailContactSegment')[0]
        except:
            email_segment = '-'
        
        try:
            addresses = credit_report.findall('Address')[0]
        except:
            addresses = np.nan
            
        try:
            score_segment = credit_report.find('ScoreSegment')
        except:
            score_segment = np.nan
            
        AC = credit_report.findall('Account')
        if len (AC)>=1:
            rows = []
            for i in AC:
                row = []
                details = i.find('Account_NonSummary_Segment_Fields')
                try:
                    ac_type = details.find('AccountType').text
                except:
                    ac_type = "-"
                row.append(ac_type)
                try:
                    ownership = details.find('OwenershipIndicator').text
                except:
                    ownership = "-"
                row.append(ownership)
                try:
                    open_date = details.find('DateOpenedOrDisbursed').text
                except:
                    open_date = "-" 
                row.append(open_date)
                try:
                    end_date = details.find('DateClosed').text
                except:
                    end_date = "-" 
                row.append(end_date)
                try:
                    last_date = details.find('DateOfLastPayment').text
                except:
                    last_date = "-"
                row.append(last_date)
                try:
                    report_date = details.find('DateReportedAndCertified').text
                except:
                    report_date = "-"
                row.append(report_date)
                try:
                    emi = details.find('EmiAmount').text
                except:
                    emi = "-"
                row.append(emi)
                try:
                    amount = details.find('HighCreditOrSanctionedAmount').text
                except:
                    amount = "-"
                row.append(amount)
                try:
                    balance = details.find('CurrentBalance').text
                except:
                    balance = "-"
                row.append(balance)
                try:
                    overdue = details.find('AmountOverdue').text
                except:
                    overdue = "-"
                row.append(overdue)
                try:
                    interest = details.find('RateOfInterest').text
                except:
                    interest = "-"
                row.append(interest)
                try:
                    tenure = details.find('RepaymentTenure').text
                except:
                    tenure = "-"
                row.append(tenure)
                try:
                    collateral_Value = details.find('ValueOfCollateral').text
                except:
                    collateral_Value = "-"
                row.append(collateral_Value)       
                try:
                    due_days1 = details.find('PaymentHistory1').text
                except:
                    due_days1 = "-"
                row.append(due_days1)
                rows.append(row)
            Cibil_Data3.extend(rows) 
        
        if len(credit_report.findall('Account'))>=1:
            accounts = credit_report.findall('Account')[0]
        else:
            accounts = np.nan
            
        enquiries = credit_report.findall('Enquiry')
        
        #NameSegment:
        name1 = name_segment.find('ConsumerName1').text
        
        try:
            name2 = name_segment.find('ConsumerName2').text
        except:
            name2 = np.nan
            
        dob = name_segment.find('DateOfBirth').text
        dob = datetime.strptime(dob,'%d%m%Y').date()
        gender = name_segment.find('Gender').text
        if int(gender) == 1:
            gender = 'Female'
        else:
            gender = 'Male'
            
        #IDSegment:
        if id_segment != '-':
            pan_no = id_segment.find('IDNumber').text
        else:
            pan_no = '-'
            
        #Telephone Segment:
        if tele_segment != '-':
            phone_no = tele_segment.find('TelephoneNumber').text
        else:
            phone_no = '-'
        
        #Email Segment:
        if email_segment != '-':
            email = email_segment.find('EmailID').text
        else:
            email = np.nan
            
        #Score Segement:
        if score_segment.find('Score').text == '000-1':
            cibilscore = int(score_segment.find('Score').text.split('-')[-1])
    
        else:
            cibilscore = int(score_segment.find('Score').text)
            
        #Address Segment:
        a1 = addresses.find('AddressLine1').text
        try:
            a2 = addresses.find('AddressLine2').text
        except:
            a2 = ''
    
        address = a1+', '+a2
        try:
            city = a2.split()[-1]
        except:
            city = '-'
    
        pin = addresses.find('PinCode').text
        
        #Account Segment:
        try:
            details = accounts.find('Account_NonSummary_Segment_Fields')
        except:
            details = '-'
            
        try:
            ac_no = details.find('AccountNumber').text
        except:
            ac_no = np.nan
            
        try:
            open_date = details.find('DateOpenedOrDisbursed').text
        except:
            open_date = np.nan
            
            
        try:
            last_date = details.find('DateOfLastPayment').text
        except:
            last_date = np.nan
        
        try:
            emi = details.find('EmiAmount').text
        except:
            emi = np.nan
    
        try:
            amount = details.find('HighCreditOrSanctionedAmount').text
        except:
            amount = np.nan
    
        try:
            balance = details.find('CurrentBalance').text
        except:
            balance = np.nan
            
        try:
            overdue = details.find('AmountOverdue').text
        except:
            overdue = 0
            
        try:
            interest = details.find('RateOfInterest').text
        except:
            interest = np.nan
            
        try:
            tenure = details.find('RepaymentTenure').text
        except:
            tenure = np.nan
            
        try:
            collateral_Value = details.find('ValueOfCollateral').text
        except:
            collateral_Value = np.nan
            
        try:
            due_days1 = details.find('PaymentHistory1').text
        except:
            due_days1 = np.nan
            
        try:
            due_days2 = details.find('PaymentHistory2').text
        except:
            due_days2 = np.nan
            
        #EnquirySegment:
        total_no_enquiries = len(enquiries)
        
        if total_no_enquiries >= 1:
            enquiry = enquiries[0]
        else:
            enquiry = np.nan
            
        try:
            last_enq_purpose = enquiry.find('EnquiryPurpose').text
        except:
            last_enq_purpose = np.nan
            
        try:
            last_enq_date = enquiry.find('DateOfEnquiryFields').text
        except:
            last_enq_date = np.nan
    
        try:
            last_enq_amt = enquiry.find('EnquiryAmount').text
        except:
            last_enq_amt = np.nan
            
        whole_data = [name1, 
                        name2,
                        dob,
                        gender,
                        pan_no,
                        phone_no,
                        email,
                        cibilscore,
                        address,
                        city,
                        pin,
                        ac_no,
                        open_date,
                        last_date,
                        amount,
                        balance,
                        int(overdue),
                        interest,
                        tenure,
                        emi,
                        collateral_Value,
                        due_days1,
                        due_days2,
                        total_no_enquiries,
                        last_enq_date,
                        last_enq_purpose,
                        last_enq_amt]    
        
        try:
            #Finding Enquiries per Month:
            enq = []
            if len(enquiries)>1:
                for i in range(len(enquiries)):
                    row = []
                    row.append(enquiries[i].find('DateOfEnquiryFields').text)
                    row.append(enquiries[i].find('EnquiryPurpose').text)
                    row.append(enquiries[i].find('EnquiryAmount').text)
                    enq.append(row)
            enq = pd.DataFrame(enq,columns=["Date","Purpose","Amount"])
            def fun(dat):
                stop = datetime.strptime(dat, "%d%m%Y").date()
                return stop
            enq['Date'] = enq['Date'].apply(fun)
            enq['Date'] = enq['Date'].astype(str)
            enq['Date'] = enq['Date'].apply(dateutil.parser.parse, dayfirst=True)
        except:
            pass
    
    else:
        whole_data = None
        
    #External Accessing    
    Cibil_Data1.extend(enq.values.tolist())
    Cibil_Data2.extend(whole_data)
        
    return whole_data,enq

bank_data = []
#This is a function to read the pdf bank statement of HDFC Bank:
def HDFC_PDF(file):
    """
    This function wil parse the HDFC PDF Statement.
    This function will return the average bank balance per month.
    """
    #Read PDF file:
    tables = tabula.read_pdf(file,pages='all')

    #Combining all tables:
    table = []
    for i in range(len(tables)):
        s1 = tables[i].values.tolist()
        table.extend(s1)


    #Removing unwanted columns:
    ex = []
    for i in range(len(tables)):
        if tables[i].shape[1] == 7:
            ex.extend(tables[i].values.tolist())
        elif tables[i].shape[1] == 6:
            table = tables[i].values.tolist()
            for i in table:
                i.append(i[5])
                i[5] = np.nan
                ex.append(i)

        elif tables[i].shape[1] == 8:
            table = tables[i].values.tolist()
            for i in table:
                del i[2]
                ex.append(i)

    #Creating dataframe:
    df = pd.DataFrame(ex,columns=['Date', 'Narration', 'Chq./Ref.No.', 'Value Dt', 'Withdrawal Amt.','Deposit Amt.', 'Closing Balance'])

    #Removing rows which having date is null:
    df = df[~df['Date'].isnull()]

    #Parsing Closing Price
    df["Closing Balance"] = df["Closing Balance"].astype(str)

    #Converting dataset into List:
    l1 = df.values.tolist()

    #Handiling Closing Balance column:
    final = []
    for i in l1:
        splits = (i[-1].split())
        if (len(splits)>1):
            i[-2] = splits[0]
            i[-1] = splits[1]
            final.append(i)
        else:
            final.append(i)

    #Creating dataframe:
    final = pd.DataFrame(final,columns=['Date', 'Narration', 'Chq/Ref.No', 'Value Dt', 'Withdrawal Amt','Deposit Amt', 'Closing Balance'])
    
    #Calculating check bounce:
    bal_list = final.iloc[:,-1].values.tolist()
    
    val = []
    for j in bal_list:
        val.append(''.join(j.split(','))) 
    val = [float(i) for i in val]
    
    bounce = 0
    for i in val:
        try:
            if i<0:
                bounce = bounce + 1
        except:
            continue
    
    #Parsing the date fields:
    final['Date'] = final['Date'].apply(dateutil.parser.parse, dayfirst=True)
    final['Value Dt'] = final['Value Dt'].apply(dateutil.parser.parse, dayfirst=True)

    #Paring prices:
    final['Closing Balance'] = final['Closing Balance'].astype(str)
    col = ['Closing Balance']
    for i in col:
        val = []
        for j in final[i]:
            val.append(''.join(j.split(',')))
        final[i] = val

    #TypeCasting Closing Balance:
    col = ['Closing Balance']
    for i in col:
        final[i] = pd.to_numeric(final[i],errors='coerce')
        

    sample = final.values.tolist()
    #Group by operation to close price:
    group = final.groupby(pd.Grouper(key='Date',freq='1M'))

    #Filtering close balance per month:
    balance_month = []
    for i in group:
        a = i[1]
        balance_month.append(a['Closing Balance'].iloc[-1])
           
    bank_data.extend(sample)
    #Closing Balance Per Month:
    return np.average(balance_month),bounce


#Loading a model:
model = pickle.load(open('model_tw_sig.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/back',methods=['POST','GET'])
def back():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    predict_request = []
    res = []
    
    #Uploading file:
    cibil_file = request.files['cibil']   
    destination = cibil_file
    cibil_data,enq = CIBIL(destination)
    
    status = request.form["martial_status"]
    married = {2750:"Married",2751:"Un Married"}
    predict_request.append(status)
    res.append(married.get(int(status)))
    
    dep = request.form["dependants"]
    predict_request.append(dep)
    res.append(dep)
    
    resi = request.form["residence"]
    residence = {2755:"Own",2756:"Rent"}
    predict_request.append(resi)
    res.append(residence.get(int(resi)))
    
    year = request.form["staying_year"]
    predict_request.append(year)
    res.append(year)
    
    #Uploading file:
    file = request.files['file']
    filename = file.filename
    extn = filename.split('.')[-1]   
    destination = file
  
    #Checking for extension of file: 
    if (extn.casefold() == 'pdf'):
        #Returned a result from a function calling:
        clobal,bounce =  HDFC_PDF(destination)
    
    if (extn.casefold() == 'xls'):
        #Loading dataset:
        df = pd.read_excel(destination)
        
        #Fetching transactions only:
        row_no = 0
        for i in df.iloc[:,0]:
            if i == 'Date':
                df = df.iloc[row_no:]
                break
            row_no = row_no+1
        
        #Set a features name:
        df.columns = ['Date', 'Narration', 'Chq./Ref.No.', 'Value Dt', 'Withdrawal Amt.','Deposit Amt.', 'Closing Balance']
        
        #Reset the Index:
        df.reset_index(drop=True, inplace=True)
        
        #Dropping first two records:
        df.drop([0,1],axis=0,inplace=True)
        
        #Reset the Index:
        df.reset_index(drop=True, inplace=True)
        
        row_no = 0
        for i in df['Date']:
            if len(str(i)) != 8:
                df = df.iloc[:row_no]
                break
            row_no = row_no + 1
            
        bal_list = df.iloc[:,-1].values.tolist()
        
        bounce = 0
        for i in bal_list:
            try:
                if i<0:
                    bounce = bounce + 1
            except:
                continue
            
        # Parsing date:
        df['Date'] = df['Date'].apply(dateutil.parser.parse, dayfirst=True)
        table = df
        
        bank_data.extend(table.values.tolist())
        
        #Group by operation to find opening and close price:
        group = table.groupby(pd.Grouper(key='Date',freq='1M'))
        
        #Filtering open and close balance per month:
        balance_month = []
        for i in group:
            a = i[1]
            balance_month.append(a['Closing Balance'].iloc[-1])
        
        clobal = (np.average(balance_month))
   
    predict_request.append(clobal)
    res.append("{:,}".format(int(clobal)))

    asset = request.form["assetvalue"]
    predict_request.append(asset)
    res.append("{:,}".format(int(asset)))
    
    cat = request.form["productcat"]
    prod_cat = {1784:"LOAN AGAINST PROPERTY",
            926:"CAR",
            912:"MULTI UTILITY VEHICLE",
            945:"VIKRAM",
            1402:"TRACTOR",
            1373:"USED VEHICLES",
            1672:"TIPPER",
            1664:"FARM EQUIPMENT",
            1541:"TWO WHEELER",
            634:"INTERMEDIATE COMMERCIAL VEHICLE",
            527:"HEAVY COMMERCIAL VEHICLE",
            528:"CONSTRUCTION EQUIPMENTS",
            529:"THREE WHEELERS",
            530:"LIGHT COMMERCIAL VEHICLES",
            531:"SMALL COMMERCIAL VEHICLE",
            738:"MEDIUM COMMERCIAL VEHICLE",
            783:"BUSES"}
    predict_request.append(cat)
    res.append(prod_cat.get(int(cat)))
    
    brand = request.form["brand"]
    brand_type = {1:"Others",
                  1360:"HONDA",
                  1542:"HERO", 
                  1544:"HMSI",
                  1547:"YAMAHA",
                  1546:"SUZUKI",
                  1647:"TVS",
                  1549:"ROYAL ENFIELD"
                  }
    predict_request.append(brand)
    res.append(brand_type.get(int(brand)))
    
    indus = request.form["industrytype"]
    ind_cat = {1782:"SALARIED",1783:"SELF EMPLOYEED",603:"AGRICULTURE",
     604:"PASSENGER TRANSPORTATION",605:"CONSTRUCTION",875:"INFRASTRUCTURE",
     876:"CEMENT",877:"OIL AND GAS",878:"GOVERNMENT CONTRACT",879:"OTHERS",658:"MINE"}
    predict_request.append(indus)
    res.append(ind_cat.get(int(indus)))
    
    tenure = request.form["tenure"]
    predict_request.append(tenure)
    res.append(tenure)
    
    instal = request.form["instalcount"]
    predict_request.append(instal)
    res.append(instal)
    
    chasasset = request.form["chasasset"]
    predict_request.append(chasasset)
    res.append("{:,}".format(int(chasasset)))
    
    chasinitial = request.form["chasinitial"]
    predict_request.append(chasinitial)
    res.append("{:,}".format(int(chasinitial)))
    
    chasfin = int(chasasset) - int(chasinitial)
    predict_request.append(chasfin)
    res.append("{:,}".format(int(chasfin)))
    
    fininter = request.form["finaninterest"]
    predict_request.append(fininter)
    res.append(fininter)
    
    interestamount = (int(chasfin)*(int(tenure)/12)*(float(fininter)))/100
    emi = (int(chasfin)+int(interestamount))/int(tenure)
    predict_request.append(int(emi))
    res.append("{:,}".format(int(emi)))
    
    inflow = request.form["totinflow"]
    predict_request.append(inflow)
    res.append("{:,}".format(int(inflow)))
    
    #Cibil Score from xml data:
    if str(cibil_data[7]) != 'nan':
        cibil = cibil_data[7]
    else:
        cibil = 0
    predict_request.append(cibil)
    res.append(cibil)
    
    age = request.form["age"]
    predict_request.append(age)
    res.append(age)
    
    #############################################
    if int(age) >= 60:
        age_score = 1
    elif int(age) >= 50:
        age_score  = 2
    elif int(age) >= 40:
        age_score = 3
    elif int(age) >= 30:
        age_score = 5
    else:
        age_score = 0   
    predict_request.append(age_score)
    res.append(age_score)
    
    
    if int(resi) == 2755:
        TOR_Score = 5
    else:
        TOR_Score = 0
    predict_request.append(TOR_Score)
    res.append(TOR_Score)
    
    if int(year) >= 3:
        NYS = 5
    elif int(year) >= 2:
        NYS = 3
    elif int(year) <= 1:
        NYS = 0
    else:
        NYS = 2
    predict_request.append(NYS)
    res.append(NYS)
    
    if int(dep) >= 2:
        Dependant_Score = 3
    else:
        Dependant_Score = 5
    predict_request.append(Dependant_Score)
    res.append(Dependant_Score)
    
    
    l2v = int((int(chasfin)*100)/int(chasasset))
    if l2v <= 60:
        L2V_Score = 5
    elif l2v <= 80:
        L2V_Score = 3
    elif l2v <=90:
        L2V_Score = 2
    else:
        L2V_Score = 0
    predict_request.append(L2V_Score)
    res.append(L2V_Score)
    
    #over 3years(5) 2Years(3) one year(2) others(0)
    stability = request.form["stability"]
    stab_cat = {
            1 :"Salaried with over 3 years",
            2 :"Salaried with over 2 years",
            3 :"Salaried with over 1 year and above",
            4 :"Others"}
    res.append(stab_cat.get(int(stability)))
    if int(stability) == 1:
        stability_score = 5
    elif int(stability) == 2:
        stability_score = 3
    elif int(stability) == 3:
        stability_score = 2
    elif int(stability) == 4:
        stability_score = 0
    predict_request.append(stability_score)
    res.append(stability_score)
    
    if int(chasfin) < int(inflow):
        salary_score = 5
    elif (int(inflow)/int(chasfin)) >= 50:
        salary_score = 4
    elif (int(inflow)/int(chasfin)) >= 25:
        salary_score = 2
    else:
        salary_score = 1
    predict_request.append(salary_score)
    res.append(salary_score)
    
    ctc = int(inflow)*12
    if (ctc == int(chasfin)):
        Borrwing_Score = 5
    elif (2*(ctc) == int(chasfin)):
        Borrwing_Score = 3
    else:
        Borrwing_Score = 0
    predict_request.append(Borrwing_Score)
    res.append(Borrwing_Score)
    
    #Cibil Score:
    if int(cibil) == 700:
        CIBIL_Score = 3
    elif int(cibil) > 700:
        CIBIL_Score = 5
    else:
        CIBIL_Score = 1
    predict_request.append(CIBIL_Score)
    res.append(CIBIL_Score)

    dpd60_point = False
    dpd30_point = True
    #Over 60DPD inall(0) Suit filed(0)60DPD in one forth of loans by value(3)less than 30DPD in all(5):
    for history in cibil_data[21:23]:
        if str(history) != 'nan':
            l1 = history
            loc = []
            for i in range(0,len(l1),3):
                loc.append(i)
    
            due = []
            i= 0
            j = i+1   
            count =0
            while count+1<len(loc):
                count = count+1
                due.append(l1[loc[i]:loc[j]])
                i = i+1
                j = j+1 
            due.append(l1[loc[j-1]:])
    
            for i in range(len(due)):
                try:
                    due[i] = int(due[i])
                except:
                    due[i] = due[i]     
    
            for i in due:
                try:
                    if i >= 60:
                        dpd60_point = True
                        break
                except:
                    continue
    
            for i in due:
                try:
                    if (i == 'XXX') or (i <= 30):
                        continue
                    else:
                        dpd30_point = False
                        break
                except:
                    continue 
        else:
            break
    
    print(dpd30_point)    
    if dpd30_point:
        predict_request.append(5)
        res.append(5)
    elif dpd60_point:
        res.append(0)
        predict_request.append(0)
    else:
        res.append(0)
        predict_request.append(0)
    
    #Similar products in three months(0) else(1):
    enquiry_point = False
    if len(enq) > 1:
        enq_list = enq.values.tolist()
        for i in enq_list:
            if i[0] > datetime.today()-timedelta(90):
                if i[1] == '13':
                    enquiry_point = True
                    break
            
    if enquiry_point:
        predict_request.append(0)
        res.append(0)
    else:
        res.append(5)
        predict_request.append(5)
    
    #Account over 2yearvintage(5) one year and above(3)over6 months(2)0thers(0):
    bank = request.form["bank_detail"]
    bank_cat = {1 :"Account over 2year",
             2:"One year and above",
             3:"Over 6 months",
             4 :"Others"}
    res.append(bank_cat.get(int(bank)))
    
    if int(bank) == 1:
        bank_score = 5
    elif int(bank) == 2:
        bank_score = 3
    elif int(bank) == 3:
        bank_score = 2
    if int(bank) == 4:
        bank_score = 0
    predict_request.append(bank_score)
    res.append(bank_score)
    

    if int(clobal) >=  (2*int(emi)):
        avg_bal_score = 5
        
    elif int(clobal) >=  int(emi):
        avg_bal_score = 4
        
    elif int(clobal) >= ((int(emi)/100)*90):
        avg_bal_score = 3
    else:
        avg_bal_score = 1
    predict_request.append(avg_bal_score)
    res.append(avg_bal_score)
    
    #5	NIL(5)  others(0) checkbounce
    if bounce > 0:
        predict_request.append(0)
        res.append(0)
    else:
        res.append(5)
        predict_request.append(5)
    
    #############################################    
    gender_dict = {'M':[0,1],'F':[1,0]}
    cate = request.form["gender"]
    if cate == 'M':
        res.append('Male')
    else:
        res.append('Female')
        
    res.append(request.form["pan"])
    
    geo_cat = {1 :"Less than 15 Km",
               2 :"More than 15 Km"}
    res.append(geo_cat.get(int(request.form["geo"])))
        
    predict_request.extend(gender_dict.get(cate))
    predict_request = list(map(float,predict_request))
    predict_request = np.array(predict_request)
    prediction = model.predict_proba([predict_request])[0][-1]
    output = int((1 - prediction)*100)
    if output < 50:
        condition = 'Risky'
    if output >= 50 and output <= 69:
        condition = 'Barely Acceptable'
    if output >= 70 and output <=89:
        condition = 'Medium'
    if output >= 90 and output <= 99:
        condition = 'Good'
    if output == 100:
        condition = 'Superior'
    print('######################################')
    if str(cibil_data[21]) == 'nan':
        cibil_due = 0
    else:
        cibil_due = cibil_data[21][0:3]
        
        
    print(len(Cibil_Data2))
    print(Cibil_Data2)
    print('######################################')
    return render_template('resultpage.html', prediction_text=output,data=res,status=condition,info=cibil_data,chk = bounce,cibil_due=cibil_due)


@app.route('/visualize_bank')
def visualize_bank():
    report = "Bank Statement Report"
    column_name = ['Date', 'Narration', 'Chq./Ref.No.', 'Value Dt', 'Withdrawal Amt.','Deposit Amt.', 'Closing Balance']
    df = pd.DataFrame(bank_data,columns=column_name)
    if df.shape[0]>1:
        for i in range(df.shape[0]):
            df["Date"][i] = df["Date"][i].strftime("%d-%m-%Y")
        df.fillna('',inplace=True)
    return render_template("bank.html", column_names=df.columns.values, row_data=list(df.values.tolist()),report = report)

@app.route('/visualize_data')
def visualize_data():
    indices1 = ["Name1","Name2","Date of Birth","Gender","PAN Number","Phone Number","Email Id","Cibil Score","Address","City","Pin Code","Account Number","Open Date","Last Date","Amount","Balance","Overdue","Interest","Tenure","EMI","Collateral Value","Due Days1","Due Days2","Total Number of Enquiries","Last_Enquired Date","Last_Enquired Purpose","Last_Enquired Amount"]
    data_list1 = []
    for i in range(len(indices1)):
        row = []
        row.append(indices1[i])
        row.append(Cibil_Data2[i])
        data_list1.append(row)
    column_name1 = ["Details","Values"]
    df1 = pd.DataFrame(data_list1,columns = column_name1)
    df1.fillna('-',inplace=True)

    #########################################
    column_name2 = ["Date","Purpose","Amount"]
    enq_cat = {"01":"Current Business Loan – Director Search",
		"02":"Current Housing Loan",
		"03":"Current Property Loan",
		"04":"Current Loan Against Shares/Securities",
		"05":"Current Personal Loan",
		"06":"Current Consumer Loan",
		"07":"Current Gold Loan",
		"08":"Current Education Loan",
		"09":"Current Loan to Professional",
		"10":"Current Credit Card",
		"11":"Current Leasing",
        "12":"Current Overdraft",
		"13":"Current Two-wheeler Loan",
		"14":"FCF Current Non-Funded Credit Facility",
		"15":"ABD Current Loan Against Bank Deposits",
		"16":"Current Fleet Card",
		"17":"Current Commercial Vehicle Loan",
		"18":"Future Telco – Wireless",
		"19":"Future Telco – Broadband",
		"20":"Future Telco – Landline",
        "31":"Current Secured Credit Card",
		"32":"Current Used Car Loan",
		"33":"Current Construction Equipment Loan",
		"34":"Current Tractor Loan",
		"35":"Current Corporate Credit Card",
		"40":"Current Microfinance – Business Loan",
		"41":"Current Microfinance – Personal Loan",
		"42":"Current Microfinance – Housing Loan",
		"43":"Current Microfinance – Other",
		"51":"Current Business Loan – General",
		"52":"LPS-SB Current Business Loan – Priority ",
		"53":"LPS-AGR Current Business Loan – Priority",
		"54":"BLPS-OTH Current Business Loan – Priority Sector – Others",
		"55":"BNFCF-GEN Current Business Non-Funded Credit Facility – General",
		"56":"BNFCF-PS-SB Current Business Non-Funded Credit Facility – Priority Secor Small Business",
        "57":"BNFCF-PS-AGR Current Business Non-Funded Credit Facility – Priority",
		"58":"BNFCF-PS-OTH Current Business Non-Funded Credit Facility – Priority",
		"59":"BLABD Current Business Loan Against Bank Deposits",
		"60":"Current Business Loan – Director Search",
		"80":"Future Microfinance Detailed Report (Applicable to Enquiry",
		"81":"Future Summary Report (Applicable to Enquiry Purpose only)",
		"88":"Current Locate Plus for Insurance (Applicable to Enquiry Purpose",
		"89":"Reserved VB OLM Retrieval Service (Applicable to Enquiry",
		"90":"Current Account Review (Applicable to Enquiry Purpose only)",
		"91":"Current Retro Enquiry (Applicable to Enquiry Purpose only)",
        "92":"Current Locate Plus (Applicable to Enquiry Purpose only)",
		"93":"Current For Individual (Applicable to Enquiry Purpose only)",
		"94":"Future Indicative Report (Applicable to Enquiry Purpose for CRS",
		"95":"Current Consumer Disclosure Report (Applicable to Enquiry",
		"96":"Future Bank OLM Retrieval Service (Applicable to Enquiry",
        "97":"Current Adviser Liability (Applicable to Enquiry Purpose only)",
		"98":"Current Secured (Account Group for Portfolio Review response)",
		"99":"Current Unsecured (Account Group for Portfolio Review",
		"00":"Current Other",
        "39":"Current Other"}
    
    if len(Cibil_Data1) >= 1:
        df2 = pd.DataFrame(Cibil_Data1,columns=column_name2)
        for i in range(df2.shape[0]):
            df2["Date"][i] = df2["Date"][i].strftime("%d-%m-%Y")
      
        for i in range(df2.shape[0]):
            df2["Purpose"][i] = enq_cat[df2["Purpose"][i]]
    else:        
        df2 = pd.DataFrame(columns=column_name2)
        
    #################################################################################
    ownership_cat = {"1":"Individual","2":"Authorised User","3":"Guarantor","4":"Joint" }
    column_name3 = ["AccountType","Owenership","DateOpened","DateClosed","DateOfLastPayment","DateReportedAndCertified","EmiAmount","SanctionedAmount","CurrentBalance","AmountOverdue","RateOfInterest","RepaymentTenure","ValueOfCollateral","PaymentHistory"]  
    if len(Cibil_Data3) >= 1:
        df3 = pd.DataFrame(Cibil_Data3,columns=column_name3)
        
        for i in range(df3.shape[0]):
            df3["AccountType"][i] = enq_cat[df3["AccountType"][i]]
            
        for i in range(df3.shape[0]):
            df3["Owenership"][i] = ownership_cat[df3["Owenership"][i]]
        
        date_cols = ["DateOpened","DateClosed","DateOfLastPayment","DateReportedAndCertified"]
        for col in date_cols: 
            for i in range(df3.shape[0]):
                if df3[col][i] == '-':
                    continue
                else:
                    df3[col][i] = datetime.strptime(df3[col][i], "%d%m%Y").date()
            
    else:
        df3 = pd.DataFrame(columns=column_name3)
    #################################################################
            
    return render_template("tabs.html",column_names1=df1.columns.values, row_data1=list(df1.values.tolist()),column_names2=df2.columns.values, row_data2=list(df2.values.tolist()),column_names3=df3.columns.values, row_data3=list(df3.values.tolist()))

if __name__ == "__main__":
    app.run(debug=True)
