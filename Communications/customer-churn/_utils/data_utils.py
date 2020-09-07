from sklearn.preprocessing import LabelEncoder, StandardScaler
import pandas as pd
import numpy as np

# Columns to ignore for model training
ignore_col = ["CustomerID", "ChurnProbability", "PredictionAccuracy"]
# Target columns
target_col = ["Churn"]

#Tenure to categorical column
def tenure_lab(telcom) :
    if telcom["Tenure"] <= 12 :
        return "Tenure_0-12"
    elif (telcom["Tenure"] > 12) & (telcom["Tenure"] <= 24 ):
        return "Tenure_12-24"
    elif (telcom["Tenure"] > 24) & (telcom["Tenure"] <= 48) :
        return "Tenure_24-48"
    elif (telcom["Tenure"] > 48) & (telcom["Tenure"] <= 60) :
        return "Tenure_48-60"
    elif telcom["Tenure"] > 60 :
        return "Tenure_gt_60"
    
def data_manipulation(telcom):
    #Replacing spaces with null values in total charges column
    telcom['TotalCharges'] = telcom["TotalCharges"].replace(" ",np.nan)

    #Dropping null values from total charges column which contain .15% missing data 
    telcom = telcom[telcom["TotalCharges"].notnull()]
    telcom = telcom.reset_index()[telcom.columns]

    #convert to float type
    telcom["TotalCharges"] = telcom["TotalCharges"].astype(float)

    #replace 'No internet service' to No for the following columns
    replace_cols = [ 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                    'TechSupport','StreamingTV', 'StreamingMovies']
    for i in replace_cols : 
        telcom[i]  = telcom[i].replace({'No internet service' : 'No'})

    #replace values
    telcom["SeniorCitizen"] = telcom["SeniorCitizen"].replace({1:"Yes",0:"No"})
    
    telcom["TenureGroup"] = telcom.apply(lambda telcom:tenure_lab(telcom), axis = 1)
    return telcom
    
def data_preprocessing(telcom):
    # categorical columns
    cat_cols = telcom.nunique()[telcom.nunique() < 6].keys().tolist()
    cat_cols = [x for x in cat_cols if x not in target_col]
    # numerical columns
    num_cols = [x for x in telcom.columns if x not in cat_cols + target_col + ignore_col]
    # Binary columns with 2 values
    bin_cols = telcom.nunique()[telcom.nunique() == 2].keys().tolist()
    # Columns more than 2 values
    multi_cols = [i for i in cat_cols if i not in bin_cols]

    # #Label encoding Binary columns
    le = LabelEncoder()
    for i in bin_cols:
        telcom[i] = le.fit_transform(telcom[i])

    # Duplicating columns for multi value columns
    telcom = pd.get_dummies(data=telcom, columns=multi_cols)

    # Scaling Numerical columns
    # transform your data such that its distribution will have a mean value 0 and standard deviation of 1
    std = StandardScaler()
    scaled = std.fit_transform(telcom[num_cols])
    scaled = pd.DataFrame(scaled, columns=num_cols)

    # dropping original values merging scaled values for numerical columns
#     df_telcom_og = telcom.copy()
    telcom = telcom.drop(columns=num_cols, axis=1)
    telcom = telcom.merge(scaled, left_index=True, right_index=True, how="left")
    return telcom