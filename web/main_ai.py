from sklearn import linear_model
import pickle
import pandas as pd
# load the model from disk
"""
filename = "C:/Users/Kahveci/Desktop/Codes/OrganDonationSystem/web/YBBLOG/ai_model/finalized_model.sav"
loaded_model = pickle.load(open(filename, 'rb'))

predict_ =loaded_model.predict([[10,0,25,1,1,1,0,55,1]])
print(predict_)
"""
def prediction(patient_profile=input("Lütfen Parametreleri Sırayla Giriniz:")):
    
    filename = "C:/Users/Kahveci/Desktop/Codes/OrganDonationSystem/web/YBBLOG/ai_model/finalized_model.sav"
    loaded_model = pickle.load(open(filename, 'rb'))
    users_input = pd.DataFrame(patient_profile)
    prediction = loaded_model.predict(users_input)
    return print(prediction)

prediction([[10,0,25,1,1,1,0,55,1]])