import dns.resolver
import pandas as pd
import time
import sys
import filter

pd.__version__

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']


filename = 'emails.txt'
#loading the file. This is just a simple file with email addresses consecutive lines
try:
    print ("Trying to open file ", filename)
    with open(filename) as f:
        domains = [line.rstrip() for line in f]
except:
    print("Error while loading", filename)
    sys.exit("IO error")
else:
    print (len(domains), "addresses loaded...starting mx lookup.\n\n")
    
time.sleep(1)
    
mxRecords = []
emailAddresses = []


#we use domain.split("@",1)[1] to seperate the domain from the email addresses
#the try-catch is necessary to avoid stopping th execution when a lookup fails.
for domain in domains:
    try:
        answers = dns.resolver.query(domain.split("@",1)[1], 'MX')
    except:
        print ("some error")
        mxRecord = "some error"
    else:
        
        mxRecord = answers[0].exchange.to_text()
    finally:
        mxRecords.append(mxRecord)
        emailAddresses.append(domain)
        print (domain)
        time.sleep(.200)

#a 200 ms pause is added for good measure
#the rest of the program uses pandas to export everything neatly to CSV. It takes to lists "mxRecords" and "emailAddresses" and converts it to a dataframe.

df = pd.DataFrame({"EmailAddress":emailAddresses,
                  "MXRecords":mxRecords})

print ("\n", str(len(emailAddresses)), "records processed") 

df.to_csv('emails.csv', index=False)

filter()