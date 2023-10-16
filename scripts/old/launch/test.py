import requests
import json

url = "http://digimate.airtel.in:15181/BULK_API/InstantJsonPush"

name = 'karthik'
username = 'pkarthkk'
password = 'karnh123@'
phone = 9652290152

payload = json.dumps({
    "keyword": "DEMO",
    "timeStamp": "1659688504",
    "dataSet": [
        {
            "UNIQUE_ID": "16596885049652",
            "MESSAGE": f"""Hi {name} , Greetings from Naan Mudhalvan. Please find your account details to login into your account. Website : https://naanmudhalvan.tn.gov.in , username : {username} , password {password}\r\nNMGOVT""",
            "OA": "NMGOVT",
            "MSISDN": "91" + str(phone),
            "CHANNEL": "SMS",
            "CAMPAIGN_NAME": "tnega_u",
            "CIRCLE_NAME": "DLT_SERVICE_IMPLICT",
            "USER_NAME": "tnega_tnsd",
            "DLT_TM_ID": "1001096933494158",
            "DLT_CT_ID": "1007269191406004910",
            "DLT_PE_ID": "1001857722001387178"
        }
    ]
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
