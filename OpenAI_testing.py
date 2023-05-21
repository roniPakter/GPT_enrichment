import os
import openai
import json
import re
import json
import pandas as pd

openai.api_key = "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"

def ask(prompt):
    response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=300,
                temperature=0,
            )
    answer = response.choices[0].text.strip()
    return answer

# This is the enriched json data structure for Victims. If we want more data we can add keys here and ChatGPT will search for them 
emptyVictimJson = {
    "post_title": "",
    "discovered": "",
    "actor": "",
    "description": "",
    "Company name":"",
    "domain":"",
    "country":"",
    "industry":"",
    "revenue":"",
    "number of employees":"",
    "enrichment":""
}

industries = "[Government/Military, Other, Finance/Banking, Manufacturing, Healthcare, Communications, Insurance/Legal, ISP/MSP, Education/Research, Retail/Wholesale, Transportation, Utilities, Software vendor, NA, Consultant, Leisure/Hospitality, SI/VAR/Distributor, Hardware vendor]"
countries = "Afghanistan, Albania, Algeria, Andorra, Angola, Antigua and Barbuda, Argentina, Armenia, Australia, Austria, Azerbaijan, Bahamas, Bahrain, Bangladesh, Barbados, Belarus, Belgium, Belize, Benin, Bhutan, Bolivia, Bosnia and Herzegovina, Botswana, Brazil, Brunei, Bulgaria, Burkina Faso, Burundi, Côte d'Ivoire, Cabo Verde, Cambodia, Cameroon, Canada, Central African Republic, Chad, Chile, China, Colombia, Comoros, Congo (Congo-Brazzaville), Costa Rica, Croatia, Cuba, Cyprus, Czechia (Czech Republic), Democratic Republic of the Congo, Denmark, Djibouti, Dominica, Dominican Republic, Ecuador, Egypt, El Salvador, Equatorial Guinea, Eritrea, Estonia, Eswatini , Ethiopia, Fiji, Finland, France, Gabon, Gambia, Georgia, Germany, Ghana, Greece, Grenada, Guatemala, Guinea, Guinea-Bissau, Guyana, Haiti, Holy See, Honduras, Hungary, Iceland, India, Indonesia, Iran, Iraq, Ireland, Israel, Italy, Jamaica, Japan, Jordan, Kazakhstan, Kenya, Kiribati, Kuwait, Kyrgyzstan, Laos, Latvia, Lebanon, Lesotho, Liberia, Libya, Liechtenstein, Lithuania, Luxembourg, Madagascar, Malawi, Malaysia, Maldives, Mali, Malta, Marshall Islands, Mauritania, Mauritius, Mexico, Micronesia, Moldova, Monaco, Mongolia, Montenegro, Morocco, Mozambique, Myanmar (formerly Burma), Namibia, Nauru, Nepal, Netherlands, New Zealand, Nicaragua, Niger, Nigeria, North Korea, North Macedonia, Norway, Oman, Pakistan, Palau, Palestine State, Panama, Papua New Guinea, Paraguay, Peru, Philippines, Poland, Portugal, Qatar, Romania, Russia, Rwanda, Saint Kitts and Nevis, Saint Lucia, Saint Vincent and the Grenadines, Samoa, San Marino, Sao Tome and Principe, Saudi Arabia, Senegal, Serbia, Seychelles, Sierra Leone, Singapore, Slovakia, Slovenia, Solomon Islands, Somalia, South Africa, South Korea, South Sudan, Spain, Sri Lanka, Sudan, Suriname, Sweden, Switzerland, Syria, Tajikistan, Tanzania, Thailand, Timor-Leste, Togo, Tonga, Trinidad and Tobago, Tunisia, Turkey, Turkmenistan, Tuvalu, Uganda, Ukraine, United Arab Emirates, United Kingdom, United States of America, Uruguay, Uzbekistan, Vanuatu, Venezuela, Vietnam, Yemen, Zambia, Zimbabwe"

filePath = 'TryChatGPT.json'
f = open('TryChatGPT.json')

# Takes the raw victims data from scraper and adds missing keys to all victims with value "N/A"
bigVictimsData = json.load(f)
victimsData = bigVictimsData
#victimsData = list(filter(lambda x: x["discovered"].startswith("2023-05-0"), bigVictimsData))
for victim in victimsData:
    for key in emptyVictimJson.keys():
        if not key in victim:
            victim[key]=""

suceededCount = 0
failedCount = 0
# Query ChatGPT for missing data
for i in range(len(victimsData)):
    print(f"{i+1} ==>")
    if victimsData[i]["enrichment"] != "":
        print("enrichedAlready")
        continue

    original = victimsData[i]
    victimFocusedJson = {
        "post_title": original["post_title"],
        "description": original["description"],
        "Company name":original["Company name"],
        "domain": original["domain"],
        "country": original["country"],
        "industry": original["industry"],
        "revenue": original["revenue"],
        "number of employees": original["number of employees"]
    }

    
    

   # extract the dictionary from random text that Chat GPT might add befomre or after the json
    try:
        result = ask("Please find accurate real business information regarding to the entity detailed in the json below."
                + "\nAdd the correlating data to the missing values to the json. If a specific value cannot be found please keep it empty."
                + "\nInsert country value representing the location of the company described in the Json only from this list:" + countries +"."
                + "\nInsert industry value correlating the company described in the Json only from this list:" + industries +"."
                + "\nThe \"revenue\" value must be an integer signifying the last known anunal revenue in millions of US dollars."
                + "\nThe \"number of employees\" value must be an integer signifying the minimal number of employees."
                + "\nIf not failed - Reply with a string designed to be converted to json with json.loads." 
                + str(victimFocusedJson))
        resultjson = json.loads(result.replace("'", '"'))
        for key in resultjson:
            original[key] = resultjson
        victimsData[i]=resultjson
        victimsData[i]["enrichment"] = "succeeded"
        suceededCount += 1
    except:
        print(f"!!! Victim {i + 1} not updated, json extraction failed.")
        victimsData[i]["enrichment"] = "failed"
        victimsData[i]["enrichmentResponeseFailedToParse"] = (result.replace("'", '"'))
        failedCount += 1
    with open(filePath, "w") as outPut:
        json.dump(victimsData, outPut)    
print(f"Failed: {failedCount} \n Succeeded: {suceededCount}")


## To save the enriched data to excel file - run this:
#
#df_json = pd.read_json('longEnrichedVictimList.json')           
#df_json.to_excel('enricghedShortVictimList_CP_Industries.xlsx')
