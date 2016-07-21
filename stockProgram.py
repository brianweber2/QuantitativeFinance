'''
Collection of functions used for sending and calculating
stock alerts.
'''

# Import required libraries
import smtplib
from twilio.rest import TwilioRestClient
import talib
from pandas_datareader import data
import numpy as np
import pandas as pd


# Function to send email using Google SMTP
def sendEmailGoogle(myEmail, myAppPassword, toEmails, message):
	myServer = 'smtp.gmail.com'
	myPortNumber = 587

	# Create SMTP object
	smtpObj = smtplib.SMTP(
		host=myServer,
		port=myPortNumber
	)

	# Start TLS encryption
	smtpObj.starttls()

	# Log in to the SMTP server
	smtpObj.login(
		user=myEmail,
		password=myAppPassword
	)

	# Send mail
	print("\nSending mail...")
	smtpObj.sendmail(
		from_addr=myEmail,
		to_addrs=toEmails,
		msg=message
	)

	# Disconnect from the SMTP server
	smtpObj.quit()


# Function to send a SMS using Twilio
def sendSMSTwilio(accountSID, token, myNumber, twilioNumber, message):
	client = TwilioRestClient(
		account=accountSID,
		token=token
	)

	# Send message
	message = client.sms.messages.create(
		to=myNumber,
		from_=twilioNumber,
		body=message
	)


# Function to calculate RSI of a stock price
def rsi(security, start_date, end_date, window_length=14):
	# Get stock data
	pricing = data.DataReader(
		name=security,
		data_source='yahoo',
		start=start_date,
		end=end_date
	)
	# Grab only adjusted close price
	security_close = pricing['Adj Close']

	# Calculate RSI
	rsi_values = talib.RSI(
		security_close.values,
		timeperiod=window_length
	)

	return pricing, rsi_values


# Function to calculate EWMA of a stock's RSI
def rsi_EWMA(rsi_values, window_length=14):
	center_of_mass = (window_length - 1) / 2
	rsi_EWMA_values = pd.ewma(rsi_values, com=center_of_mass, ignore_na=True)

	return rsi_EWMA_values


