from twilio.rest import Client

account_sid = 'AC05f13d37a52ff70d14825daa3980203c'
auth_token = '2facde9dd9d873542bb2c5540cb8f735'
client = Client(account_sid, auth_token)

message = client.messages.create(
    from_='whatsapp:+14155238886',
    body='Testing2222',
    to='whatsapp:+6582264058'

)

print(message.sid)
